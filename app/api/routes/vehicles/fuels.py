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

from fastapi import APIRouter, Depends

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.get_id_from_path import get_fuel_id_from_path
from app.models.schemas.service import ServiceInResponse, ListOfServicesInResponse

router = APIRouter()


@router.post(
    "",
    response_model=ServiceInResponse,
    name="vehicle:create-fuel"
)
async def create_fuel(
        user_id: int = Depends(get_current_user_authorizer()),
):
    pass


@router.get(
    "",
    response_model=ListOfServicesInResponse,
    name="fuels:get-all-fuels"
)
async def get_fuels(
        user_id: int = Depends(get_current_user_authorizer()),
) -> ListOfServicesInResponse:
    pass


@router.get(
    "/{fuel_id}",
    response_model=ServiceInResponse,
    name="fuels:get-fuel"
)
async def get_fuel_by_id(
        fuel_id: int = Depends(get_fuel_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
):
    pass


@router.put(
    "/{fuel_id}",
    response_model=ServiceInResponse,
    name="vehicle:update-fuel"
)
async def update_fuel_by_id(
        fuel_id: int = Depends(get_fuel_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
):
    pass


@router.delete(
    "/{fuel_id}",
    response_model=ServiceInResponse,
    name="vehicle:delete-fuel"
)
async def delete_fuel_by_id(
        fuel_id: int = Depends(get_fuel_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
):
    pass
