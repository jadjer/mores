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

from app.database.repositories.profiles import ProfilesRepository
from app.database.repositories.users import UsersRepository
from app.models.domain.profile import Profile
from app.models.domain.user import UserInDB
from app.models.schemas.user import UserInResponse


@pytest.mark.asyncio
@pytest.fixture(params=("", "value", "Token value", "JWT value", "Bearer value"))
def wrong_authorization_header(request) -> str:
    return request.param


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "users:get-current-user"), ("PUT", "users:update-current-user")),
)
async def test_user_can_not_access_own_profile_if_not_logged_in(
    app: FastAPI,
    client: AsyncClient,
    test_profile: Profile,
    api_method: str,
    route_name: str,
) -> None:
    response = await client.request(api_method, app.url_path_for(route_name))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "users:get-current-user"), ("PUT", "users:update-current-user")),
)
async def test_user_can_not_retrieve_own_profile_if_wrong_token(
    app: FastAPI,
    client: AsyncClient,
    test_profile: Profile,
    api_method: str,
    route_name: str,
    wrong_authorization_header: str,
) -> None:
    response = await client.request(
        api_method,
        app.url_path_for(route_name),
        headers={"Authorization": wrong_authorization_header},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_user_can_retrieve_own_profile(
    app: FastAPI, authorized_client: AsyncClient, test_profile: Profile, token: str
) -> None:
    response = await authorized_client.get(app.url_path_for("users:get-current-user"))
    assert response.status_code == status.HTTP_200_OK

    user_profile = UserInResponse(**response.json())
    assert user_profile.user.email == test_profile.u.email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_field, update_value",
    (
        ("username", "new_username"),
        ("email", "new_email@email.com"),
        ("bio", "new bio"),
        ("image", "http://testhost.com/imageurl"),
    ),
)
async def test_user_can_update_own_profile(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
    token: str,
    update_value: str,
    update_field: str,
) -> None:
    response = await authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {update_field: update_value}},
    )
    assert response.status_code == status.HTTP_200_OK

    user_profile = UserInResponse(**response.json()).dict()
    assert user_profile["user"][update_field] == update_value


@pytest.mark.asyncio
async def test_user_can_change_password(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_profile: Profile,
    token: str,
    session: Session,
) -> None:
    response = await authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {"password": "new_password"}},
    )
    assert response.status_code == status.HTTP_200_OK
    user_profile = UserInResponse(**response.json())

    profiles_repo = ProfilesRepository(session)
    profile = await profiles_repo.get_profile_by_username(
        username=user_profile.user.username
    )

    assert user.check_password("new_password")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "credentials_part, credentials_value",
    (("username", "taken_username"), ("email", "taken@email.com")),
)
async def test_user_can_not_take_already_used_credentials(
    app: FastAPI,
    authorized_client: AsyncClient,
    session: Session,
    token: str,
    credentials_part: str,
    credentials_value: str,
) -> None:
    user_dict = {
        "username": "not_taken_username",
        "password": "password",
        "email": "free_email@email.com",
    }
    user_dict.update({credentials_part: credentials_value})
    users_repo = UsersRepository(session)
    await users_repo.create_user(**user_dict)

    response = await authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {credentials_part: credentials_value}},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
