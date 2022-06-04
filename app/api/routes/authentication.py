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

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.api.dependencies.database import get_repository
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.errors import EntityDoesNotExists
from app.database.repositories.profiles import ProfilesRepository
from app.database.repositories.users import UsersRepository
from app.models.domain.profile import Profile
from app.models.schemas.user import (
    UserInCreate,
    UserInLogin,
    UserWithToken,
    UserInResponseWithToken
)
from app.resources import strings
from app.services import jwt
from app.services.authentication import (
    check_email_is_taken,
    check_username_is_taken,
)

router = APIRouter()


@router.post(
    "/login",
    response_model=UserInResponseWithToken,
    name="auth:login",
)
async def login(
        user_login: UserInLogin = Body(..., embed=True, alias="user"),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserInResponseWithToken:
    incorrect_credentials = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.INCORRECT_LOGIN_INPUT)

    try:
        profile: Profile = await profiles_repo.get_profile_by_username(user_login.username)
    except EntityDoesNotExists as exception:
        raise incorrect_credentials from exception

    user = await users_repo.get_user_by_id(profile.user_id)
    if not user.check_password(user_login.password):
        raise incorrect_credentials

    token = jwt.create_access_token_for_user(
        user_id=user.id,
        username=profile.username,
        secret_key=settings.secret_key.get_secret_value()
    )

    return UserInResponseWithToken(user=UserWithToken(token=token, **user.__dict__))


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserInResponseWithToken,
    name="auth:register",
)
async def register(
        user_create: UserInCreate = Body(..., embed=True, alias="user"),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        profile_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserInResponseWithToken:
    email_taken_error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.EMAIL_TAKEN)
    username_taken_error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)

    if await check_email_is_taken(users_repo, user_create.email):
        raise email_taken_error

    if await check_username_is_taken(profile_repo, user_create.username):
        raise username_taken_error

    user = await users_repo.create_user(email=user_create.email, password=user_create.password)
    profile = await profile_repo.create_profile(user.id, username=user_create.username)

    token = jwt.create_access_token_for_user(
        user_id=user.id,
        username=profile.username,
        secret_key=settings.secret_key.get_secret_value()
    )

    return UserInResponseWithToken(user=UserWithToken(token=token, **user.__dict__))
