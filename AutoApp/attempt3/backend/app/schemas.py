from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    filename: str
    uploaded_at: datetime
    replaced: bool

    model_config = ConfigDict(from_attributes=True)


class WordCountResponse(BaseModel):
    filename: str
    word: str
    count: int


class UploadDetailsResponse(BaseModel):
    filename: str
    uploaded_at: datetime
    raw_text: str
    normalized_text: str

    model_config = ConfigDict(from_attributes=True)


class UploadFileListResponse(BaseModel):
    filenames: list[str]
