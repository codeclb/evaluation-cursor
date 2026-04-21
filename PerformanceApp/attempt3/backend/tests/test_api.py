from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_upload_rejects_non_txt() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/files/upload",
            files={"file": ("input.csv", b"a,b", "text/csv")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only .txt files are supported"


def test_upload_and_count_with_fake_repository(monkeypatch) -> None:
    file_id = uuid4()
    uploaded_at = datetime.now(timezone.utc)

    class FakeRepo:
        def __init__(self, _db):
            pass

        def get_file_by_filename(self, _filename):
            return None

        def create_file_with_transformation(self, **kwargs):
            return SimpleNamespace(
                id=file_id,
                filename=kwargs["filename"],
                uploaded_at=uploaded_at,
            )

        def get_transformation(self, requested_file_id):
            if requested_file_id != file_id:
                return None
            return SimpleNamespace(word_frequency={"hello": 2, "world": 1})

        def get_file(self, requested_file_id):
            if requested_file_id != file_id:
                return None
            return SimpleNamespace(
                id=file_id,
                filename="sample.txt",
                uploaded_at=uploaded_at,
                transformation=SimpleNamespace(),
            )

        def list_files(self):
            return [
                SimpleNamespace(id=file_id, filename="sample.txt", uploaded_at=uploaded_at),
            ]

    monkeypatch.setattr("app.main.FileRepository", FakeRepo)

    with TestClient(app) as client:
        upload_response = client.post(
            "/files/upload",
            files={"file": ("sample.txt", b"hello hello world", "text/plain")},
        )

        assert upload_response.status_code == 200
        uploaded_payload = upload_response.json()
        assert UUID(uploaded_payload["file_id"]) == file_id

        metadata_response = client.get(f"/files/{file_id}")
        assert metadata_response.status_code == 200
        assert metadata_response.json()["filename"] == "sample.txt"

        count_response = client.get(f"/files/{file_id}/count", params={"word": "Hello"})
        assert count_response.status_code == 200
        assert count_response.json()["count"] == 2


def test_count_rejects_multi_word_query(monkeypatch) -> None:
    class FakeRepo:
        def __init__(self, _db):
            pass

        def get_transformation(self, _file_id):
            return SimpleNamespace(word_frequency={"hello": 2})

    monkeypatch.setattr("app.main.FileRepository", FakeRepo)

    with TestClient(app) as client:
        response = client.get(f"/files/{uuid4()}/count", params={"word": "two words"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Query must contain a single word"
