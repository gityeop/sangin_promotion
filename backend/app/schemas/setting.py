from pydantic import BaseModel, conint


class SettingRead(BaseModel):
    passing_score: int
    num_questions: int
    num_options: int

    class Config:
        orm_mode = True


class SettingUpdate(BaseModel):
    passing_score: conint(ge=0, le=100)
    num_questions: conint(ge=1)
    num_options: conint(ge=2)
