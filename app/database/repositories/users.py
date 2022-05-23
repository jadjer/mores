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

from sqlalchemy import select

from app.database.errors import EntityDoesNotExist
from app.database.repositories.base import BaseRepository
from app.models.domain.user import User, UserInDB
from app.database.models import UserModel


class UsersRepository(BaseRepository):

    async def get_user_by_email(self, email: str) -> UserInDB:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            return UserInDB(**user.__dict__)

        raise EntityDoesNotExist("user with email {0} does not exist".format(email))

    async def get_user_by_username(self, username: str) -> UserInDB:
        query = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            return UserInDB(**user.__dict__)

        raise EntityDoesNotExist("user with username {0} does not exist".format(username))

    async def create_user(self, username: str, email: str, password: str) -> UserInDB:
        user = UserInDB(username=username, email=email)
        user.change_password(password)

        new_user = UserModel(
            username=user.username,
            email=user.email,
            password=user.password,
        )

        self.session.add(new_user)
        await self.session.commit()

        return user

    async def update_user(self,
                          user: User,
                          username: Optional[str] = None,
                          email: Optional[str] = None,
                          password: Optional[str] = None,
                          bio: Optional[str] = None,
                          image: Optional[str] = None) -> UserInDB:

        user_in_db = await self.get_user_by_username(username=user.username)

        user_in_db.username = username or user_in_db.username
        user_in_db.email = email or user_in_db.email
        user_in_db.bio = bio or user_in_db.bio
        user_in_db.image = image or user_in_db.image

        if password:
            user_in_db.change_password(password)

        self.session.add(user_in_db)
        await self.session.commit()

        return user_in_db
