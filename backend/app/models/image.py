from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class ImageType(str, PyEnum):
    CORRECT = "correct"
    INCORRECT = "incorrect"


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, nullable=False)
    type = Column(Enum(ImageType), nullable=False)
    used_in_session = Column(Boolean, default=False, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    uploader = relationship("User")

    def __repr__(self) -> str:
        return f"<Image {self.id} ({self.type})>"
