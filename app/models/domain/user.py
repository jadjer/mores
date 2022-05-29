#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from enum import Enum

from pydantic import HttpUrl, EmailStr

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.rwmodel import RWModel
from app.services import security


class Gender(Enum):
    UNDEFINED = "undefined"
    MALE = "male"
    FEMALE = "female"


class UserShort(RWModel):
    username: str
    image: HttpUrl


class UserLong(UserShort):
    email: EmailStr
    first_name: str
    second_name: str
    last_name: str
    gender: Gender = Gender.UNDEFINED
    age: int
    phone: str


class User(UserLong):
    is_admin: bool = False
    is_blocked: bool = False


class UserInDB(IDModelMixin, DateTimeModelMixin, User):
    salt: str = ""
    password: str = ""

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.password = security.get_password_hash(self.salt + password)
