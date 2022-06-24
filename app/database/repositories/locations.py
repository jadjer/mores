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

        return await self.get_location_by_id(new_location.id)

    async def get_location_by_id(self, location_id: int) -> Location:
        location_in_db = await self._get_location_model_by_id(location_id)

        return self._convert_location_model_to_location(location_in_db)

    async def update_location_by_id(
            self,
            location_id: int,
            *,
            description: Optional[str] = None,
            latitude: Optional[float] = None,
            longitude: Optional[float] = None,
    ) -> Location:
        location_in_db = await self._get_location_model_by_id(location_id)
        location_in_db.description = description or location_in_db.description
        location_in_db.latitude = latitude or location_in_db.latitude
        location_in_db.longitude = longitude or location_in_db.longitude

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return await self.get_location_by_id(location_id)

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

    @staticmethod
    def _convert_location_model_to_location(location_model: LocationModel) -> Location:
        return Location(
            id=location_model.id,
            description=location_model.description,
            latitude=location_model.latitude,
            longitude=location_model.longitude,
        )
