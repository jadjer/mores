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

from typing import List, Optional

from app.models.domain.location import Location
from app.models.domain.service import Service
from app.models.schemas.rwschema import RWSchema


class ListOfServicesInResponse(RWSchema):
    services: List[Service]
    count: int


class ServiceInResponse(RWSchema):
    service: Service


class ServiceInCreate(RWSchema):
    location: Location
    service_type_id: int
    mileage: int
    price: float


class ServiceInUpdate(RWSchema):
    location: Optional[Location] = None
    service_type_id: Optional[int] = None
    mileage: Optional[int] = None
    price: Optional[float] = None
