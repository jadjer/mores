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

from typing import List, Optional

from app.models.domain.fuel import Fuel, FuelType
from app.models.domain.location import Location
from app.models.schemas.rwschema import RWSchema


class ListOfFuelsInResponse(RWSchema):
    fuels: List[Fuel]
    count: int


class FuelInResponse(RWSchema):
    fuel: Fuel


class FuelInCreate(RWSchema):
    quantity: float
    price: float
    mileage: int
    fuel_type: FuelType
    is_full: bool
    location: Location


class FuelInUpdate(RWSchema):
    quantity: Optional[float] = None
    price: Optional[float] = None
    mileage: Optional[int] = None
    fuel_type: Optional[FuelType] = None
    is_full: Optional[bool] = None
    location: Optional[Location] = None
