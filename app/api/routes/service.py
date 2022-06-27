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
    Depends,
    Body,
    HTTPException,
    status, Path
)

from app.api.dependencies.authentication import (
    get_current_user_authorizer,
    get_current_user_is_admin,
)
from app.api.dependencies.database import get_repository
from app.database.errors import EntityCreateError, EntityDoesNotExists
from app.database.repositories.api_keys import ApiKeysRepository
from app.models.schemas.api_keys import (
    KeyInResponse,
    KeyInCreate,
    ListOfKeysInResponse, KeyInUpdate
)
from app.resources import strings

router = APIRouter()


@router.post(
    "/keys",
    response_model=KeyInResponse,
    name="service:create-api-key",
    dependencies=[
        Depends(get_current_user_is_admin())
    ]
)
async def create_api_key(
        api_key_create: KeyInCreate = Body(..., embed=True, alias="api_key"),
        api_keys_repo: ApiKeysRepository = Depends(get_repository(ApiKeysRepository)),
) -> KeyInResponse:
    api_key_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.API_KEY_CREATE_ERROR
    )

    try:
        api_key = await api_keys_repo.create_key(api_key_create.description)
    except EntityCreateError as exception:
        raise api_key_create_error from exception

    return KeyInResponse(key=api_key)


@router.get(
    "/keys/{api_key_id}",
    response_model=KeyInResponse,
    name="service:mark-key-as-revoked",
    dependencies=[
        Depends(get_current_user_is_admin())
    ]
)
async def mark_key_as_revoked(
        api_key_id: int = Path(..., ge=1),
        api_keys_repo: ApiKeysRepository = Depends(get_repository(ApiKeysRepository)),
) -> KeyInResponse:
    api_key_update_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.API_KEY_UPDATE_ERROR
    )

    try:
        api_keys = await api_keys_repo.mark_key_as_revoked(api_key_id)
    except EntityDoesNotExists as exception:
        raise api_key_update_error from exception

    return KeyInResponse(key=api_keys)


@router.get(
    "/keys",
    response_model=ListOfKeysInResponse,
    name="service:get-all-keys",
    dependencies=[
        Depends(get_current_user_is_admin())
    ]
)
async def get_all_keys(
        api_keys_repo: ApiKeysRepository = Depends(get_repository(ApiKeysRepository)),
) -> ListOfKeysInResponse:
    api_keys = await api_keys_repo.get_keys()

    return ListOfKeysInResponse(keys=api_keys, count=len(api_keys))
