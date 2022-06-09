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

import pytest

from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.database.repositories.users import UsersRepository
from app.models.domain.profile import Profile
from app.models.domain.user import UserInDB

pytestmark = pytest.mark.asyncio


async def test_user_success_registration(
    app: FastAPI, client: AsyncClient, session: Session
) -> None:
    email, username, password = "test@test.com", "username", "password"
    registration_json = {
        "user": {"email": email, "username": username, "password": password}
    }
    response = await client.post(
        app.url_path_for("auth:register"), json=registration_json
    )
    assert response.status_code == status.HTTP_201_CREATED

    async with session as conn:
        repo = UsersRepository(conn)
        user = await repo.get_user_by_email(email=email)
        assert user.email == email
        # assert user.username == username
        assert user.check_password(password)


@pytest.mark.parametrize(
    "credentials_part, credentials_value",
    (("username", "free_username"), ("email", "free-email@tset.com")),
)
async def test_failed_user_registration_when_some_credentials_are_taken(
    app: FastAPI,
    client: AsyncClient,
    test_profile: Profile,
    credentials_part: str,
    credentials_value: str,
) -> None:
    registration_json = {
        "user": {
            "email": "test@test.com",
            "username": "username",
            "password": "password",
        }
    }
    registration_json["user"][credentials_part] = credentials_value

    response = await client.post(
        app.url_path_for("auth:register"), json=registration_json
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
