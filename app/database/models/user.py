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

from sqlalchemy import Boolean, Column, Integer, String, Enum

from app.database.base import Base
from app.models.domain.user import Gender


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    salt = Column(String)

    first_name = Column(String, nullable=True)
    second_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    gender = Column(Enum(Gender), default=Gender.UNDEFINED)
    age = Column(Integer, nullable=True)
    phone = Column(String, unique=True)
    image = Column(String, nullable=True)

    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
