import logging
from uuid import UUID

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.logging_config import setup_logging
from app.repositories.file_repository import FileRepository
from app.schemas import FileListItemResponse, FileMetadataResponse, UploadResponse, WordCountResponse
from app.services.text_processing import build_word_frequency, normalize_text, normalize_word

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="TXT Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/files", response_model=list[FileListItemResponse])
def list_files(db: Session = Depends(get_db)) -> list[FileListItemResponse]:
    repo = FileRepository(db)
    records = repo.list_files()
    return [
        FileListItemResponse(file_id=r.id, filename=r.filename, uploaded_at=r.uploaded_at)
        for r in records
    ]


@app.post("/files/upload", response_model=UploadResponse)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadResponse:
    filename = file.filename or ""
    logger.info("Upload received: %s", filename)

    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    repo = FileRepository(db)
    if repo.get_file_by_filename(filename) is not None:
        logger.info("Duplicate upload rejected: %s", filename)
        raise HTTPException(status_code=409, detail=f"A file named '{filename}' has already been uploaded")

    raw_bytes = file.file.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text") from exc

    normalized_text = normalize_text(raw_text)
    word_frequency = build_word_frequency(normalized_text)

    created = repo.create_file_with_transformation(
        filename=filename,
        raw_text=raw_text,
        normalized_text=normalized_text,
        word_frequency=word_frequency,
    )

    logger.info("Upload complete: file_id=%s, filename=%s", created.id, created.filename)
    return UploadResponse(file_id=created.id, filename=created.filename, uploaded_at=created.uploaded_at)


@app.get("/files/{file_id}", response_model=FileMetadataResponse)
def get_file_metadata(file_id: UUID, db: Session = Depends(get_db)) -> FileMetadataResponse:
    repo = FileRepository(db)
    file_record = repo.get_file(file_id)
    if file_record is None:
        raise HTTPException(status_code=404, detail="File not found")

    return FileMetadataResponse(
        file_id=file_record.id,
        filename=file_record.filename,
        uploaded_at=file_record.uploaded_at,
        has_transformation=file_record.transformation is not None,
    )


@app.get("/files/{file_id}/count", response_model=WordCountResponse)
def count_word_occurrences(
    file_id: UUID,
    word: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> WordCountResponse:
    normalized_word = normalize_word(word)
    if not normalized_word or " " in normalized_word:
        raise HTTPException(status_code=400, detail="Query must contain a single word")

    repo = FileRepository(db)
    transformation = repo.get_transformation(file_id)
    if transformation is None:
        raise HTTPException(status_code=404, detail="File not found")

    count = transformation.word_frequency.get(normalized_word, 0)
    logger.info("Word count query: file_id=%s, word=%s, count=%d", file_id, normalized_word, count)
    return WordCountResponse(file_id=file_id, word=normalized_word, count=count)
