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
from app.database.errors import EntityDoesNotExist
from app.database.repositories.users import UsersRepository
from app.models.schemas.user import (
    UserInCreate,
    UserInLogin,
    UserInResponse,
    UserWithToken,
)
from app.resources import strings
from app.services import jwt
from app.services.authentication import check_email_is_taken, check_username_is_taken

router = APIRouter()


@router.post("/login", response_model=UserInResponse, name="auth:login")
async def login(
        user_login: UserInLogin = Body(..., embed=True, alias="user"),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserInResponse:
    wrong_login_error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.INCORRECT_LOGIN_INPUT)

    try:
        user = await users_repo.get_user_by_username(user_login.username)
    except EntityDoesNotExist as existence_error:
        raise wrong_login_error from existence_error

    if not user.check_password(user_login.password):
        raise wrong_login_error

    token = jwt.create_access_token_for_user(
        user,
        str(settings.secret_key.get_secret_value()),
    )

    return UserInResponse(
        user=UserWithToken(
            first_name=user.first_name,
            second_name=user.second_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            gender=user.gender,
            age=user.age,
            phone=user.phone,
            is_admin=user.is_admin,
            is_blocked=user.is_blocked,
            image=user.image,
            token=token
        )
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserInResponse, name="auth:register")
async def register(
        user_create: UserInCreate = Body(..., embed=True, alias="user"),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserInResponse:
    if await check_username_is_taken(users_repo, user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.USERNAME_TAKEN,
        )

    if await check_email_is_taken(users_repo, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.EMAIL_TAKEN,
        )

    user = await users_repo.create_user(**user_create.dict())

    token = jwt.create_access_token_for_user(
        user,
        str(settings.secret_key.get_secret_value()),
    )

    return UserInResponse(
        user=UserWithToken(
            first_name=user.first_name,
            second_name=user.second_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            gender=user.gender,
            age=user.age,
            phone=user.phone,
            is_admin=user.is_admin,
            is_blocked=user.is_blocked,
            image=user.image,
            token=token
        )
    )
