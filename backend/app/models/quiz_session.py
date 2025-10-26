from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_set = Column(JSON, nullable=False)
    score = Column(Integer, nullable=True)
    passed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_retest = Column(Boolean, default=False, nullable=False)
    submitted_at = Column(DateTime, nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<QuizSession {self.id} user={self.user_id} score={self.score}>"
