from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    file_id: UUID
    filename: str
    uploaded_at: datetime


class FileMetadataResponse(BaseModel):
    file_id: UUID
    filename: str
    uploaded_at: datetime
    has_transformation: bool


class FileListItemResponse(BaseModel):
    file_id: UUID
    filename: str
    uploaded_at: datetime


class WordCountResponse(BaseModel):
    file_id: UUID
    word: str = Field(..., min_length=1)
    count: int = Field(..., ge=0)
