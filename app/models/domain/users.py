from typing import Optional
from enum import Enum

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.rwmodel import RWModel
from app.services import security


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class User(RWModel):
    first_name: str
    second_name: Optional[str]
    last_name: str
    username: str
    email: str
    gender: Gender
    age: int
    phone: str
    is_admin: bool = False
    is_blocked: bool = False
    image: Optional[str] = None


class UserInDB(IDModelMixin, DateTimeModelMixin, User):
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)
