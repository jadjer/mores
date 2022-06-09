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

from typing import Optional

from app.database.errors import (
    EntityDoesNotExists,
    EntityDeleteError, EntityCreateError, EntityUpdateError,
)
from app.database.models import LocationModel
from app.database.repositories.base import BaseRepository
from app.models.domain.location import Location


class LocationsRepository(BaseRepository):

    async def create_location(self, description: str, latitude: float, longitude: float) -> Location:
        new_location = LocationModel()
        new_location.description = description
        new_location.latitude = latitude
        new_location.longitude = longitude

        self.session.add(new_location)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Location(**new_location.__dict__)

    async def get_location_by_id(self, location_id: int) -> Location:
        location = await self._get_location_model_by_id(location_id)

        return Location(**location.__dict__)

    async def update_location_by_id(
            self,
            location_id: int,
            description: Optional[str] = None,
            latitude: Optional[float] = None,
            longitude: Optional[float] = None,
    ) -> Location:
        location = await self._get_location_model_by_id(location_id)
        location.description = description or location.description
        location.latitude = latitude or location.latitude
        location.longitude = longitude or location.longitude

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Location(**location.__dict__)

    async def delete_location_by_id(self, location_id: int) -> None:
        location = await self._get_location_model_by_id(location_id)

        try:
            await self.session.delete(location)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_location_model_by_id(self, location_id: int) -> LocationModel:
        location: LocationModel = await self.session.get(LocationModel, location_id)
        if not location:
            raise EntityDoesNotExists

        return location
