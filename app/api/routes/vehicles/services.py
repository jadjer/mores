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
from app.database.errors import EntityCreateError
from app.database.repositories.services import ServicesRepository
from app.models.schemas.service import (
    ServiceInResponse,
    ListOfServicesInResponse,
    ServiceInCreate,
)
from app.resources import strings

router = APIRouter()


@router.post(
    "",
    response_model=ServiceInResponse,
    name="services:create-service"
)
async def create_service(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        service_create: ServiceInCreate = Body(..., alias="service"),
        user_id: int = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    service_not_created = HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.SERVICE_CREATE_ERROR)

    try:
        service = await services_repo.create_service(vehicle_id, **service_create.__dict__)
    except EntityCreateError as exception:
        raise service_not_created from exception

    return ServiceInResponse(service=service)


@router.get(
    "",
    response_model=ListOfServicesInResponse,
    name="services:get-all-services"
)
async def get_services(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ListOfServicesInResponse:
    services = await services_repo.get_services_for_all_vehicles(user_id)
    return ListOfServicesInResponse(vehicles=vehicles, count=len(vehicles))


@router.get(
    "/{service_id}",
    response_model=ServiceInResponse,
    name="services:get-service"
)
async def get_service_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    pass


@router.put(
    "/{service_id}",
    response_model=ServiceInResponse,
    name="services:update-vehicle"
)
async def update_service_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    pass


@router.delete(
    "/{service_id}",
    name="services:delete-vehicle",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_by_id(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> None:
    pass
