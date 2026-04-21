from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


def create_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_upload_and_count_flow():
    client = create_test_client()
    response = client.post(
        "/uploads",
        files={"file": ("sample.txt", b"One fish two fish red fish blue fish", "text/plain")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "sample.txt"
    assert payload["replaced"] is False

    count_response = client.get("/uploads/count", params={"filename": "sample.txt", "word": "fish"})
    assert count_response.status_code == 200
    assert count_response.json()["count"] == 4


def test_upload_replaces_existing_filename():
    client = create_test_client()
    first_upload = client.post(
        "/uploads",
        files={"file": ("replace.txt", b"alpha alpha", "text/plain")},
    )
    second_upload = client.post(
        "/uploads",
        files={"file": ("replace.txt", b"alpha beta", "text/plain")},
    )
    assert first_upload.status_code == 200
    assert first_upload.json()["replaced"] is False
    assert second_upload.status_code == 200
    assert second_upload.json()["replaced"] is True
    count_response = client.get("/uploads/count", params={"filename": "replace.txt", "word": "alpha"})
    assert count_response.status_code == 200
    assert count_response.json()["count"] == 1


def test_list_uploaded_filenames():
    client = create_test_client()
    client.post("/uploads", files={"file": ("b.txt", b"bbb", "text/plain")})
    client.post("/uploads", files={"file": ("a.txt", b"aaa", "text/plain")})

    response = client.get("/uploads/files")
    assert response.status_code == 200
    assert response.json()["filenames"] == ["a.txt", "b.txt"]


def test_rejects_non_txt_file():
    client = create_test_client()
    response = client.post(
        "/uploads",
        files={"file": ("sample.csv", b"a,b,c", "text/csv")},
    )
    assert response.status_code == 400
