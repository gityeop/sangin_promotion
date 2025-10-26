from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.models.image import ImageType


class ImageBase(BaseModel):
    file_url: HttpUrl
    type: ImageType


class ImageCreate(ImageBase):
    uploaded_by: Optional[int]


class ImageRead(ImageBase):
    id: int
    used_in_session: bool

    class Config:
        orm_mode = True
