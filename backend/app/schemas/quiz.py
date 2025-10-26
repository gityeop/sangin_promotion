from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class QuizOption(BaseModel):
    image_id: int
    file_url: str


class QuizQuestion(BaseModel):
    question_id: str
    options: List[QuizOption]


class QuizRequest(BaseModel):
    session_id: int = Field(..., description="Quiz session identifier")
    questions: List[QuizQuestion]


class QuizSubmission(BaseModel):
    session_id: int
    answers: List["QuizAnswer"]


class QuizAnswer(BaseModel):
    question_id: str
    selected_image_id: int


class QuizResult(BaseModel):
    session_id: int
    score: int
    passed: bool


QuizSubmission.update_forward_refs(QuizAnswer=QuizAnswer)
