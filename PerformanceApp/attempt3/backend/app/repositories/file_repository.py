import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import FileRecord, FileTransformation

logger = logging.getLogger(__name__)


class FileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_file_with_transformation(
        self,
        *,
        filename: str,
        raw_text: str,
        normalized_text: str,
        word_frequency: dict[str, int],
    ) -> FileRecord:
        file_record = FileRecord(filename=filename, raw_text=raw_text)
        transformation = FileTransformation(
            normalized_text=normalized_text,
            word_frequency=word_frequency,
        )
        file_record.transformation = transformation

        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        logger.debug("Persisted file %s with transformation (id=%s)", file_record.filename, file_record.id)
        return file_record

    def list_files(self) -> list[FileRecord]:
        records = self.db.query(FileRecord).order_by(FileRecord.uploaded_at.desc()).all()
        logger.debug("list_files: returned %d records", len(records))
        return records

    def get_file_by_filename(self, filename: str) -> FileRecord | None:
        record = self.db.query(FileRecord).filter(FileRecord.filename == filename).first()
        logger.debug("get_file_by_filename(%s): %s", filename, "found" if record else "not found")
        return record

    def get_file(self, file_id: UUID) -> FileRecord | None:
        record = self.db.query(FileRecord).filter(FileRecord.id == file_id).first()
        logger.debug("get_file(%s): %s", file_id, "found" if record else "not found")
        return record

    def get_transformation(self, file_id: UUID) -> FileTransformation | None:
        record = (
            self.db.query(FileTransformation)
            .filter(FileTransformation.file_id == file_id)
            .first()
        )
        logger.debug("get_transformation(%s): %s", file_id, "found" if record else "not found")
        return record
