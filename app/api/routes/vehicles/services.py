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

from fastapi import APIRouter, status, Depends, Body

from app.api.dependencies.database import get_repository
from app.api.dependencies.services import get_service_id_from_path
from app.api.dependencies.authentication import get_current_user_authorizer
from app.database.repositories.services import ServicesRepository
from app.models.domain.user import UserInDB
from app.models.schemas.service import ServiceInResponse, ListOfServicesInResponse, ServiceInCreate

router = APIRouter()


@router.get("", response_model=ListOfServicesInResponse, name="services:get-all-services")
async def get_services(
        user: UserInDB = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ListOfServicesInResponse:
    vehicles = await services_repo.get_services(user)
    return ListOfServicesInResponse(vehicles=vehicles, count=len(vehicles))


@router.post("", response_model=ServiceInResponse, name="services:create-vehicle")
async def create_service(
        service_create: ServiceInCreate = Body(..., alias="service"),
        user: UserInDB = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    pass


@router.get("/{service_id}", response_model=ServiceInResponse, name="services:get-service")
async def get_service(
        service_id: int = Depends(get_service_id_from_path),
        user: UserInDB = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    pass


@router.put("/{service_id}", response_model=ServiceInResponse, name="services:update-vehicle")
async def update_service(
        service_id: int = Depends(get_service_id_from_path),
        user: UserInDB = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    pass


@router.delete("/{service_id}", name="services:delete-vehicle")
async def delete_service(
        service_id: int = Depends(get_service_id_from_path),
        user: UserInDB = Depends(get_current_user_authorizer()),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> None:
    pass
