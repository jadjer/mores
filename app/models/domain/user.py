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

from typing import Optional
from enum import Enum

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.rwmodel import RWModel
from app.services import security


class Gender(Enum):
    UNDEFINED = 1
    MALE = 2
    FEMALE = 3


class User(RWModel):
    first_name: Optional[str]
    second_name: Optional[str]
    last_name: Optional[str]
    username: str
    email: str
    gender: Optional[Gender] = Gender.UNDEFINED
    age: Optional[int]
    phone: Optional[str]
    image: Optional[str] = None
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
