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

from pydantic import EmailStr
from sqlalchemy import select

from app.database.errors import UserDoesNotExists, UserCreateError, UserUpdateError
from app.database.repositories.base import BaseRepository
from app.models.domain.user import UserInDB
from app.database.models import UserModel


class UsersRepository(BaseRepository):

    async def create_user(self, *, email: EmailStr, password: str) -> UserInDB:
        user: UserInDB = UserInDB(email=email)
        user.change_password(password)

        new_user = UserModel()
        new_user.email = user.email
        new_user.salt = user.salt
        new_user.password = user.password

        try:
            self.session.add(new_user)
            await self.session.commit()
        except Exception as exception:
            raise UserCreateError from exception

        user.id = new_user.id

        return user

    async def get_user_by_id(self, user_id: int) -> UserInDB:
        user_in_db: UserModel = await self._get_user_model_by_id(user_id)
        if not user_in_db:
            raise UserDoesNotExists

        return UserInDB(**user_in_db.__dict__)

    async def get_user_by_email(self, email: str) -> UserInDB:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)

        user = result.scalars().first()
        if not user:
            raise UserDoesNotExists

        return UserInDB(**user.__dict__)

    async def update_user(
            self,
            user: UserInDB,
            *,
            email: Optional[str] = None,
            password: Optional[str] = None,
    ) -> UserInDB:
        if password:
            user.change_password(password)

        user_in_db: UserModel = await self._get_user_model_by_id(user.id)
        user_in_db.email = email or user_in_db.email
        user_in_db.password = password or user_in_db.password

        try:
            await self.session.commit()
        except Exception as exception:
            raise UserUpdateError from exception

        return UserInDB(**user_in_db.__dict__)

    async def _get_user_model_by_id(self, user_id: int) -> UserModel:
        user = await self.session.get(UserModel, user_id)
        if not user:
            raise UserDoesNotExists

        return user
