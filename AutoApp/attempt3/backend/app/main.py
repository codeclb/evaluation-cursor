import os
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from .models import Upload, init_db
from .schemas import UploadDetailsResponse, UploadFileListResponse, UploadResponse, WordCountResponse
from .text_processing import build_word_frequency, normalize_text

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("txt_analyzer.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting TXT Analyzer API")
    init_db()
    logger.info("Database initialization complete")
    yield


app = FastAPI(title="TXT Analyzer API", lifespan=lifespan)

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def healthcheck() -> dict[str, str]:
    logger.debug("Healthcheck requested")
    return {"status": "ok"}


@app.post("/uploads", response_model=UploadResponse)
async def create_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    raw_bytes = await file.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text") from exc

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    normalized_text = normalize_text(raw_text)
    word_freq = build_word_frequency(normalized_text)
    normalized_filename = file.filename.strip()

    existing_uploads = db.query(Upload).filter(Upload.filename == normalized_filename).all()
    replaced = len(existing_uploads) > 0
    if existing_uploads:
        logger.info("Replacing %d existing upload record(s) for filename '%s'", len(existing_uploads), normalized_filename)
        for existing_upload in existing_uploads:
            db.delete(existing_upload)
        db.commit()

    upload = Upload(
        filename=normalized_filename,
        raw_text=raw_text,
        normalized_text=normalized_text,
        word_freq_json=word_freq,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    logger.info(
        "Stored upload for filename '%s' with %d unique words",
        normalized_filename,
        len(word_freq),
    )
    logger.debug("Upload metadata filename=%s uploaded_at=%s", upload.filename, upload.uploaded_at)
    return UploadResponse(
        filename=upload.filename,
        uploaded_at=upload.uploaded_at,
        replaced=replaced,
    )


@app.get("/uploads/count", response_model=WordCountResponse)
def get_word_count(
    filename: str = Query(..., min_length=1),
    word: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    upload = db.query(Upload).filter(Upload.filename == filename).first()
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found for filename")

    normalized_word = normalize_text(word)
    if not normalized_word:
        raise HTTPException(status_code=400, detail="Word must contain alphanumeric characters")

    count = int(upload.word_freq_json.get(normalized_word, 0))
    logger.debug(
        "Word lookup filename='%s' word='%s' count=%d",
        filename,
        normalized_word,
        count,
    )
    return WordCountResponse(filename=filename, word=normalized_word, count=count)


@app.get("/uploads/details", response_model=UploadDetailsResponse)
def get_upload_details(filename: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.filename == filename).first()
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found for filename")
    logger.debug("Details requested for filename='%s'", filename)
    return upload


@app.get("/uploads/files", response_model=UploadFileListResponse)
def list_upload_files(db: Session = Depends(get_db)):
    filenames = [row[0] for row in db.query(Upload.filename).distinct().order_by(Upload.filename.asc()).all()]
    logger.debug("Listed %d filenames", len(filenames))
    return UploadFileListResponse(filenames=filenames)
