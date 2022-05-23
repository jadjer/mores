from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl

from app.models.domain.user import User
from app.models.schemas.rwschema import RWSchema


class UserInLogin(RWSchema):
    username: str
    password: str


class UserInCreate(UserInLogin):
    email: EmailStr


class UserInUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[HttpUrl] = None


class UserWithToken(User):
    token: str


class UserInResponse(RWSchema):
    user: UserWithToken
