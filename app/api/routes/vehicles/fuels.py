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
    Depends,
    Body,
    status,
    HTTPException
)

from app.api.dependencies.database import get_repository
from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.get_id_from_path import (
    get_vehicle_id_from_path,
    get_fuel_id_from_path,
)
from app.database.errors import (
    EntityCreateError,
    EntityDoesNotExists,
    EntityUpdateError,
    EntityDeleteError,
)
from app.database.repositories.fuels import FuelsRepository
from app.database.repositories.vehicles import VehiclesRepository
from app.models.schemas.fuel import (
    FuelInResponse,
    ListOfFuelsInResponse,
    FuelInCreate,
    FuelInUpdate,
)
from app.resources import strings
from app.services.vehicles import (
    update_vehicle_mileage,
    check_mileage_increases,
)

router = APIRouter()


@router.post(
    "",
    response_model=FuelInResponse,
    name="fuels:create-fuel",
)
async def create_fuel(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        fuel_create: FuelInCreate = Body(..., alias="fuel"),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> FuelInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    fuel_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.FUEL_CREATE_ERROR
    )

    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    if not await check_mileage_increases(vehicles_repo, vehicle_id, user_id, fuel_create.mileage):
        raise vehicle_mileage_reduce

    try:
        fuel = await fuels_repo.create_fuel_by_vehicle_id(vehicle_id, **fuel_create.__dict__)
    except EntityCreateError as exception:
        raise fuel_create_error from exception

    await update_vehicle_mileage(vehicles_repo, vehicle_id, user_id, fuel_create.mileage)

    return FuelInResponse(fuel=fuel)


@router.get(
    "",
    response_model=ListOfFuelsInResponse,
    name="fuels:get-all-fuels"
)
async def get_fuels(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> ListOfFuelsInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )

    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    fuels = await fuels_repo.get_fuels_by_vehicle_id(vehicle_id)
    return ListOfFuelsInResponse(fuels=fuels, count=len(fuels))


@router.get(
    "/{fuel_id}",
    response_model=FuelInResponse,
    name="fuels:get-fuel"
)
async def get_fuel_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        fuel_id: int = Depends(get_fuel_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> FuelInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    fuel_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.FUEL_DOES_NOT_EXIST_ERROR
    )

    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    try:
        fuel = await fuels_repo.get_fuel_by_id_and_vehicle_id(fuel_id, vehicle_id)
    except EntityDoesNotExists as exception:
        raise fuel_not_found from exception

    return FuelInResponse(fuel=fuel)


@router.put(
    "/{fuel_id}",
    response_model=FuelInResponse,
    name="fuels:update-fuel"
)
async def update_reminder_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        fuel_id: int = Depends(get_fuel_id_from_path),
        fuel_update: FuelInUpdate = Body(..., alias="fuel"),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> FuelInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    fuel_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.FUEL_DOES_NOT_EXIST_ERROR
    )
    fuel_update_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.FUEL_UPDATE_ERROR
    )
    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    if fuel_update.mileage and not await check_mileage_increases(
            vehicles_repo, vehicle_id, user_id, fuel_update.mileage
    ):
        raise vehicle_mileage_reduce

    try:
        fuel = await fuels_repo.update_fuel_by_id_and_vehicle_id(
            fuel_id,
            vehicle_id,
            **fuel_update.__dict__
        )
    except EntityDoesNotExists as exception:
        raise fuel_not_found from exception
    except EntityUpdateError as exception:
        raise fuel_update_error from exception

    if fuel_update.mileage:
        await update_vehicle_mileage(vehicles_repo, vehicle_id, user_id, fuel_update.mileage)

    return FuelInResponse(fuel=fuel)


@router.delete(
    "/{fuel_id}",
    name="fuels:delete-fuel",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_fuel_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        fuel_id: int = Depends(get_fuel_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> None:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    fuel_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.FUEL_DOES_NOT_EXIST_ERROR
    )
    fuel_delete_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.FUEL_DELETE_ERROR
    )
    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    try:
        await fuels_repo.delete_fuel_by_id_and_vehicle_id(fuel_id, vehicle_id)
    except EntityDoesNotExists as exception:
        raise fuel_not_found from exception
    except EntityDeleteError as exception:
        raise fuel_delete_error from exception
