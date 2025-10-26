from pydantic import BaseModel, constr

from app.models.user import UserRole


class UserBase(BaseModel):
    employee_id: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=1)


class UserCreate(UserBase):
    role: UserRole = UserRole.USER


class UserLogin(UserBase):
    pass


class UserRead(UserBase):
    id: int
    role: UserRole
    can_retake: bool

    class Config:
        orm_mode = True
