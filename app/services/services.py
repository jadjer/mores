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
from app.database.repositories.services import ServicesRepository


async def check_service_is_exist(repo: ServicesRepository, service_id: int, vehicle_id: int) -> bool:
    try:
        await repo.get_service_by_id_and_vehicle_id(service_id, vehicle_id)
    except EntityDoesNotExists:
        return False

    return True
