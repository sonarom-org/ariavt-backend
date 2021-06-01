
from typing import Optional
from pydantic import BaseModel


class ImageIn(BaseModel):
    text: str
    relative_path: str


class Image(ImageIn):
    id: int


class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    id: int
    hashed_password: str
