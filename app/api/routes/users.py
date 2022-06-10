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

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.repositories.users import UsersRepository
from app.models.domain.user import User
from app.models.schemas.user import (
    UserInResponse,
    UserInUpdate,
)
from app.resources import strings
from app.services.authentication import (
    check_phone_is_valid,
    check_phone_is_taken,
    check_username_is_taken,
)

router = APIRouter()


@router.get("", response_model=UserInResponse, name="users:get-current-user")
async def get_current_user(
        user: User = Depends(get_current_user_authorizer()),
) -> UserInResponse:
    return UserInResponse(user=user)


@router.put("", response_model=UserInResponse, name="users:update-current-user")
async def update_current_user(
        user_update: UserInUpdate = Body(..., embed=True, alias="user"),
        user: User = Depends(get_current_user_authorizer()),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserInResponse:
    phone_invalid = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.PHONE_NUMBER_INVALID_ERROR)
    phone_taken = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.PHONE_TAKEN)
    username_taken = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)

    if user_update.phone and user_update.phone != user.phone:
        if not check_phone_is_valid(user_update.phone):
            raise phone_invalid

        if await check_phone_is_taken(users_repo, user_update.phone):
            raise phone_taken

    if user_update.username and user_update.username != user.username:
        if await check_username_is_taken(users_repo, user_update.username):
            raise username_taken

    user_in_db = await users_repo.update_user_by_user(
        user,
        username=user_update.username,
        phone=user_update.phone,
        password=user_update.password
    )

    return UserInResponse(user=user_in_db)
