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

from os import environ

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.posts import PostsRepository
from app.database.repositories.profiles import ProfilesRepository
from app.models.domain.post import Post
from app.models.domain.profile import Profile
from app.services import jwt


@pytest.fixture
def app() -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
async def session(app: FastAPI) -> AsyncSession:
    from app.database.events import connect_to_db
    from app.core.config import get_app_settings

    settings = get_app_settings()
    session = await connect_to_db(app, settings)

    return session


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(
            app=app,
            base_url="http://localhost:10000",
            headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def authorization_prefix() -> str:
    from app.core.config import get_app_settings

    settings = get_app_settings()
    jwt_token_prefix = settings.jwt_token_prefix

    return jwt_token_prefix


@pytest.fixture
async def test_profile(session: AsyncSession) -> Profile:
    return await ProfilesRepository(session).create_profile_and_user(
        username="username",
        email="test@test.com",
        password="password",
    )


@pytest.fixture
async def test_post(test_profile: Profile, session: AsyncSession) -> Post:
    posts_repo = PostsRepository(session)

    return await posts_repo.create_post_by_user_id(
        user_id=test_profile.user_id,
        title="Test Slug",
        description="Slug for tests",
        thumbnail="",
        body="Test " * 100,
    )


@pytest.fixture
def token(test_profile: Profile) -> str:
    return jwt.create_access_token_for_user(
        user_id=test_profile.user_id,
        username=test_profile.username,
        secret_key=environ["SECRET_KEY"]
    )


@pytest.fixture
def authorized_client(client: AsyncClient, token: str, authorization_prefix: str) -> AsyncClient:
    client.headers = {
        "Authorization": f"{authorization_prefix} {token}",
        **client.headers,
    }
    return client
