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

from fastapi import APIRouter, status

from app.models.domain import Service
from app.models.schemas.service import ServiceInResponse, ListOfServicesInResponse

router = APIRouter()


@router.get("", response_model=ListOfServicesInResponse, name="vehicle:get-all-vehicles")
async def get_vehicles() -> ListOfServicesInResponse:
    pass


@router.get("/{type_id}", response_model=ServiceInResponse, name="vehicle:get-vehicle")
async def get_vehicles(type_id: int):
    pass


@router.post("", response_model=ServiceInResponse, name="vehicle:create-vehicle")
async def create_vehicle():
    pass


@router.put("/{type_id}", response_model=ServiceInResponse, name="vehicle:update-vehicle")
async def create_vehicle(type_id: int):
    pass


@router.delete("/{type_id}", response_model=ServiceInResponse, name="vehicle:delete-vehicle")
async def delete_vehicle(type_id: int):
    pass
