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
from app.api.dependencies.vehicles import get_vehicle_id_from_path
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.user import UserInDB
from app.models.schemas.vehicle import (
    VehicleInResponse,
    ListOfVehiclesInResponse,
    VehicleInCreate,
    VehicleInUpdate,
)
from app.resources import strings
from app.services.vehicles import (
    check_vehicle_is_exist,
    check_vim_is_taken,
    check_registration_plate_is_taken,
)

router = APIRouter()


@router.post(
    "",
    response_model=VehicleInResponse,
    name="vehicles:create-vehicle"
)
async def create_vehicle(
        vehicle_create: VehicleInCreate = Body(..., embed=True, alias="vehicle"),
        user: UserInDB = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    if await check_vim_is_taken(vehicles_repo, vehicle_create.vin):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.VEHICLE_CONFLICT_VIN_ERROR)

    if await check_registration_plate_is_taken(vehicles_repo, vehicle_create.registration_plate):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.VEHICLE_CONFLICT_REGISTRATION_PLATE_ERROR)

    vehicle = await vehicles_repo.create_vehicle(user=user, **vehicle_create.__dict__)
    return VehicleInResponse(vehicle=vehicle)


@router.get(
    "",
    response_model=ListOfVehiclesInResponse,
    name="vehicles:get-my-vehicles"
)
async def get_vehicles(
        user: UserInDB = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> ListOfVehiclesInResponse:
    vehicles = await vehicles_repo.get_vehicles(user)
    return ListOfVehiclesInResponse(vehicles=vehicles, count=len(vehicles))


@router.get(
    "/{vehicle_id}",
    response_model=VehicleInResponse,
    name="vehicles:get-vehicle"
)
async def get_vehicle(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user: UserInDB = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    if not await check_vehicle_is_exist(vehicles_repo, user, vehicle_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR)

    vehicle = await vehicles_repo.get_vehicle_by_id(user=user, vehicle_id=vehicle_id)
    return VehicleInResponse(vehicle=vehicle)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleInResponse,
    name="vehicles:update-vehicle"
)
async def update_vehicle(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        vehicle_update: VehicleInUpdate = Body(..., embed=True, alias="vehicle"),
        user: UserInDB = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    if not await check_vehicle_is_exist(vehicles_repo, user, vehicle_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR)

    if await check_vim_is_taken(vehicles_repo, vehicle_update.vin):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.VEHICLE_CONFLICT_VIN_ERROR)

    if await check_registration_plate_is_taken(vehicles_repo, vehicle_update.registration_plate):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.VEHICLE_CONFLICT_REGISTRATION_PLATE_ERROR)

    vehicle = await vehicles_repo.update_vehicle(user=user, vehicle_id=vehicle_id, **vehicle_update.__dict__)
    return VehicleInResponse(vehicle=vehicle)


@router.delete(
    "/{vehicle_id}",
    name="vehicles:delete-vehicle"
)
async def delete_vehicle(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user: UserInDB = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> None:
    if not await check_vehicle_is_exist(vehicles_repo, user, vehicle_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR)

    await vehicles_repo.delete_vehicle(user=user, vehicle_id=vehicle_id)
