from __future__ import annotations

from sqlalchemy import Column, Integer

from app.models.base import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    passing_score = Column(Integer, nullable=False, default=70)
    num_questions = Column(Integer, nullable=False, default=10)
    num_options = Column(Integer, nullable=False, default=10)
