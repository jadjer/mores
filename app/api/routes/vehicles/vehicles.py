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
    status,
    Depends,
    Body,
    HTTPException,
)

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_id_from_path import get_vehicle_id_from_path
from app.database.errors import (
    EntityDeleteError,
    EntityCreateError,
    EntityDoesNotExists,
    EntityUpdateError,
)
from app.database.repositories.vehicles import VehiclesRepository
from app.models.schemas.vehicle import (
    VehicleInResponse,
    ListOfVehiclesInResponse,
    VehicleInCreate,
    VehicleInUpdate,
)
from app.resources import strings
from app.services.vehicles import (
    check_mileage_increases,
    update_vehicle_mileage,
)

router = APIRouter()


@router.post(
    "",
    response_model=VehicleInResponse,
    name="vehicles:create-vehicle"
)
async def create_vehicle(
        vehicle_create: VehicleInCreate = Body(..., embed=True, alias="vehicle"),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    vin_reg_plate_exist = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.VEHICLE_CONFLICT_VIN_OR_REG_PLATE
    )

    try:
        vehicle = await vehicles_repo.create_vehicle_by_user_id(user_id, **vehicle_create.__dict__)
    except EntityCreateError as exception:
        raise vin_reg_plate_exist from exception

    return VehicleInResponse(vehicle=vehicle)


@router.get(
    "",
    response_model=ListOfVehiclesInResponse,
    name="vehicles:get-my-vehicles"
)
async def get_vehicles(
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> ListOfVehiclesInResponse:
    vehicles = await vehicles_repo.get_vehicles_by_user_id(user_id)
    return ListOfVehiclesInResponse(vehicles=vehicles, count=len(vehicles))


@router.get(
    "/{vehicle_id}",
    response_model=VehicleInResponse,
    name="vehicles:get-vehicle"
)
async def get_vehicle_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )

    try:
        vehicle = await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    return VehicleInResponse(vehicle=vehicle)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleInResponse,
    name="vehicles:update-vehicle"
)
async def update_vehicle_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        vehicle_update: VehicleInUpdate = Body(..., embed=True, alias="vehicle"),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    vehicle_vin_reg_plate_exist = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.VEHICLE_CONFLICT_VIN_OR_REG_PLATE
    )
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )

    if vehicle_update.mileage and not await check_mileage_increases(
            vehicles_repo, vehicle_id, user_id, vehicle_update.mileage
    ):
        raise vehicle_mileage_reduce

    try:
        vehicle = await vehicles_repo.update_vehicle_by_id_and_user_id(vehicle_id, user_id, **vehicle_update.__dict__)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception
    except EntityUpdateError as exception:
        raise vehicle_vin_reg_plate_exist from exception

    if vehicle_update.mileage:
        await update_vehicle_mileage(vehicles_repo, vehicle_id, user_id, vehicle_update.mileage)

    return VehicleInResponse(vehicle=vehicle)


@router.delete(
    "/{vehicle_id}",
    name="vehicles:delete-vehicle",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vehicle_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> None:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )

    try:
        await vehicles_repo.delete_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception
    except EntityDeleteError as exception:
        raise vehicle_not_found from exception
