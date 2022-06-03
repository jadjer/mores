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

from app.database.errors import EntityDoesNotExists
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.user import UserInDB


async def check_vehicle_is_exist(repo: VehiclesRepository, user: UserInDB, vehicle_id: int) -> bool:
    try:
        await repo.get_vehicle_by_id(user, vehicle_id)
    except EntityDoesNotExists:
        return False

    return True


async def check_vim_is_taken(repo: VehiclesRepository, vin: str) -> bool:
    try:
        await repo.get_vehicle_by_vin(vin)
    except EntityDoesNotExists:
        return False

    return True


async def check_registration_plate_is_taken(repo: VehiclesRepository, registration_plate: str) -> bool:
    try:
        await repo.get_vehicle_by_registration_plate(registration_plate)
    except EntityDoesNotExists:
        return False

    return True


async def check_user_is_owner(repo: VehiclesRepository, user: UserInDB, vehicle_id: int) -> bool:
    return await check_vehicle_is_exist(repo, user, vehicle_id)
