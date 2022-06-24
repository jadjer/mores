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

from enum import Enum

from app.models.common import (
    IDModelMixin,
    DateTimeModelMixin,
)
from app.models.domain.location import Location


class FuelType(Enum):
    PETROL_92 = "petrol_92"
    PETROL_95 = "petrol_95"
    PETROL_98 = "petrol_98"
    PETROL_100 = "petrol_100"
    DIESEL = "diesel"
    GAS = "gas"
    ELECTRICITY = "electricity"


class Fuel(IDModelMixin, DateTimeModelMixin):
    fuel_type: FuelType
    quantity: float
    price: float
    mileage: int
    is_full: bool
    location: Location
