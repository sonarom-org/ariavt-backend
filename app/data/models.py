
from typing import Optional
from pydantic import BaseModel


class ImageIn(BaseModel):
    text: Optional[str]
    relative_path: str
    title: Optional[str]


class Image(ImageIn):
    id: int
    user_id: int


class User(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None
    role: str


class UserInDB(User):
    hashed_password: str
