from datetime import datetime

from pydantic import BaseModel


class SessionResult(BaseModel):
    session_id: int
    employee_id: str
    name: str
    score: int | None
    passed: bool
    created_at: datetime
    submitted_at: datetime | None
    is_retest: bool

    class Config:
        orm_mode = True
