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

from pydantic import EmailStr, HttpUrl
from sqlalchemy import select, update

from app.database.errors import EntityDoesNotExist
from app.database.repositories.base import BaseRepository
from app.models.domain.user import UserInDB, Gender
from app.database.models import UserModel


class UsersRepository(BaseRepository):

    async def get_user_by_id(self, user_id: int) -> UserInDB:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)

        user = result.scalars().first()
        if not user:
            raise EntityDoesNotExist("user with id {0} does not exist".format(user_id))

        return UserInDB(**user.__dict__)

    async def get_user_by_email(self, email: str) -> UserInDB:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)

        user = result.scalars().first()
        if not user:
            raise EntityDoesNotExist("user with email {0} does not exist".format(email))

        return UserInDB(**user.__dict__)

    async def get_user_by_username(self, username: str) -> UserInDB:
        query = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(query)

        user = result.scalars().first()
        if not user:
            raise EntityDoesNotExist("user with username {0} does not exist".format(username))

        return UserInDB(**user.__dict__)

    async def create_user(self, *, username: str, email: EmailStr, password: str) -> UserInDB:
        user_in_db = UserInDB(username=username, email=email)
        user_in_db.change_password(password)

        user = UserModel(
            username=user_in_db.username,
            email=user_in_db.email,
            password=user_in_db.password,
            salt=user_in_db.salt
        )

        self.session.add(user)
        await self.session.commit()

        user_in_db.id = user.id

        return user_in_db

    async def update_user(
            self,
            *,
            user: UserInDB,
            username: Optional[str] = None,
            email: Optional[str] = None,
            password: Optional[str] = None,
            first_name: Optional[str] = None,
            second_name: Optional[str] = None,
            last_name: Optional[str] = None,
            gender: Optional[Gender] = None,
            age: Optional[int] = None,
            phone: Optional[str] = None,
            image: Optional[HttpUrl] = None,
    ) -> UserInDB:

        user_in_db = await self.get_user_by_id(user.id)
        user_in_db.username = username or user_in_db.username
        user_in_db.email = email or user_in_db.email
        user_in_db.first_name = first_name or user_in_db.first_name
        user_in_db.second_name = second_name or user_in_db.second_name
        user_in_db.last_name = last_name or user_in_db.last_name
        user_in_db.gender = gender or user_in_db.gender
        user_in_db.age = age or user_in_db.age
        user_in_db.phone = phone or user_in_db.phone
        user_in_db.image = image or user_in_db.image

        if password:
            user_in_db.change_password(password)

        query = update(UserModel).where(UserModel.id == user_in_db.id).values(
            username=user_in_db.username,
            email=user_in_db.email,
            password=user_in_db.password,
            first_name=user_in_db.first_name,
            second_name=user_in_db.second_name,
            last_name=user_in_db.last_name,
            gender=user_in_db.gender,
            age=user_in_db.age,
            phone=user_in_db.phone,
            image=user_in_db.image,
        )

        await self.session.execute(query)
        await self.session.commit()

        return user_in_db
