from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from .database import Base, engine


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, unique=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    raw_text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=False)
    word_freq_json = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
