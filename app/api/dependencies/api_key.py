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

from typing import (
    Callable,
    Optional
)

from fastapi import (
    Depends,
    HTTPException,
    Security,
    requests,
    status,
)
from fastapi.security import APIKeyHeader
from fastapi.exceptions import HTTPException as FastapiHTTPException

from app.api.dependencies.database import get_repository
from app.database.repositories.api_keys import ApiKeysRepository
from app.resources import strings

HEADER_KEY = "X-Api-Key"


class ApiKeyHeader(APIKeyHeader):
    async def __call__(self, request: requests.Request) -> Optional[str]:
        try:
            return await super().__call__(request)
        except FastapiHTTPException as original_auth_exc:
            raise HTTPException(status_code=original_auth_exc.status_code, detail=strings.AUTHENTICATION_REQUIRED)


def get_api_key() -> Callable:
    return _get_api_key


async def _get_api_key(
        api_key: str = Security(ApiKeyHeader(name=HEADER_KEY)),
        api_keys_repo: ApiKeysRepository = Depends(get_repository(ApiKeysRepository)),
) -> str:
    if await api_keys_repo.is_exists_key(api_key):
        return api_key

    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=strings.API_KEY_ERROR)
