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
    get_service_id_from_path,
)
from app.database.errors import (
    EntityCreateError,
    EntityDoesNotExists,
    EntityUpdateError,
    EntityDeleteError,
)
from app.database.repositories.services import ServicesRepository
from app.database.repositories.vehicles import VehiclesRepository
from app.models.schemas.service import (
    ServiceInResponse,
    ListOfServicesInResponse,
    ServiceInCreate, ServiceInUpdate,
)
from app.resources import strings
from app.services.vehicles import (
    update_vehicle_mileage,
    check_mileage_increases,
)

router = APIRouter()


@router.post(
    "",
    response_model=ServiceInResponse,
    name="services:create-service",
    dependencies=[
        Depends(get_current_user_authorizer())
    ]
)
async def create_service(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        service_create: ServiceInCreate = Body(..., alias="service"),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    service_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.SERVICE_CREATE_ERROR
    )

    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    if not await check_mileage_increases(vehicles_repo, vehicle_id, user_id, service_create.mileage):
        raise vehicle_mileage_reduce

    try:
        service = await services_repo.create_service_by_vehicle_id(vehicle_id, **service_create.__dict__)
    except EntityCreateError as exception:
        raise service_create_error from exception

    await update_vehicle_mileage(vehicles_repo, vehicle_id, user_id, service_create.mileage)

    return ServiceInResponse(service=service)


@router.get(
    "",
    response_model=ListOfServicesInResponse,
    name="services:get-all-services"
)
async def get_services(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ListOfServicesInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )

    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    services = await services_repo.get_services_by_vehicle_id(vehicle_id)
    return ListOfServicesInResponse(services=services, count=len(services))


@router.get(
    "/{service_id}",
    response_model=ServiceInResponse,
    name="services:get-service"
)
async def get_service_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    service_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.SERVICE_DOES_NOT_EXIST_ERROR
    )

    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    try:
        service = await services_repo.get_service_by_id_and_vehicle_id(service_id, vehicle_id)
    except EntityDoesNotExists as exception:
        raise service_not_found from exception

    return ServiceInResponse(service=service)


@router.put(
    "/{service_id}",
    response_model=ServiceInResponse,
    name="services:update-service"
)
async def update_service_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        service_update: ServiceInUpdate = Body(..., alias="service"),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    service_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.SERVICE_DOES_NOT_EXIST_ERROR
    )
    service_update_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.SERVICE_UPDATE_ERROR
    )
    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    if service_update.mileage and not await check_mileage_increases(
            vehicles_repo, vehicle_id, user_id, service_update.mileage
    ):
        raise vehicle_mileage_reduce

    try:
        service = await services_repo.update_service_by_id_and_vehicle_id(
            service_id,
            vehicle_id,
            **service_update.__dict__
        )
    except EntityDoesNotExists as exception:
        raise service_not_found from exception
    except EntityUpdateError as exception:
        raise service_update_error from exception

    if service_update.mileage:
        await update_vehicle_mileage(vehicles_repo, vehicle_id, user_id, service_update.mileage)

    return ServiceInResponse(service=service)


@router.delete(
    "/{service_id}",
    name="services:delete-vehicle",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> None:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )
    service_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.SERVICE_DOES_NOT_EXIST_ERROR
    )
    service_delete_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.SERVICE_DELETE_ERROR
    )
    try:
        await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user_id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    try:
        await services_repo.delete_service_by_id_and_vehicle_id(service_id, vehicle_id)
    except EntityDoesNotExists as exception:
        raise service_not_found from exception
    except EntityDeleteError as exception:
        raise service_delete_error from exception
