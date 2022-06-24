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

from app.models.domain.vehicle import Vehicle
from app.models.schemas.rwschema import RWSchema


class ListOfVehiclesInResponse(RWSchema):
    vehicles: List[Vehicle]
    count: int


class VehicleInResponse(RWSchema):
    vehicle: Vehicle


class VehicleInCreate(RWSchema):
    brand: str
    model: str
    gen: int
    year: int
    color: str
    mileage: int
    vin: str
    registration_plate: str
    name: str


class VehicleInUpdate(RWSchema):
    brand: Optional[str] = None
    model: Optional[str] = None
    gen: Optional[int] = None
    year: Optional[int] = None
    color: Optional[str] = None
    mileage: Optional[int] = None
    vin: Optional[str] = None
    registration_plate: Optional[str] = None
    name: Optional[str] = None
