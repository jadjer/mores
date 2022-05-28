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

from fastapi import APIRouter, status, Body, Depends

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.repositories.locations import LocationsRepository
from app.models.domain import User
from app.models.schemas.location import LocationInCreate, LocationInResponse

router = APIRouter()


@router.post(
    "",
    response_model=LocationInResponse,
    name="locations:create-location",
)
async def create_location(
        location_create: LocationInCreate = Body(..., embed=True, alias="geo"),
        user: User = Depends(get_current_user_authorizer()),
        locations_repo: LocationsRepository = Depends(get_repository(LocationsRepository)),
) -> LocationInResponse:
    geo = await locations_repo.create_location(**location_create)


@router.get(
    "/{location_id}",
    response_model=LocationInResponse,
    name="locations:get-location",
)
async def get_location(geo_id: int) -> LocationInResponse:
    pass


@router.put(
    "/{location_id}",
    response_model=LocationInResponse,
    name="locations:update-location",
)
async def update_location(geo_id: int) -> LocationInResponse:
    pass


@router.delete(
    "/{location_id}",
    response_model=LocationInResponse,
    name="locations:delete-location",
)
async def delete_location(geo_id: int) -> LocationInResponse:
    pass
