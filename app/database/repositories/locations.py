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

from sqlalchemy import select

from app.database.errors import EntityDoesNotExist
from app.database.models import LocationModel
from app.database.repositories.base import BaseRepository
from app.models.domain.location import Location


class LocationsRepository(BaseRepository):

    async def create_location(
            self,
            *,
            name: str,
            description: str,
            latitude: float,
            longitude: float,
    ) -> Location:
        location_in_db = LocationModel(
            name=name,
            description=description,
            latitude=latitude,
            longitude=longitude,
        )

        self.session.add(location_in_db)
        await self.session.commit()

        return self._convert_model_to_location(location_in_db)

    async def get_location(self, location_id: int) -> Location:
        query = select(LocationModel).where(LocationModel.id == location_id)
        result = await self.session.execute(query)

        location_in_db = result.scalars().first()
        if not location_in_db:
            raise EntityDoesNotExist("location with id {0} does not exist".format(location_id))

        return self._convert_model_to_location(location_in_db)

    @staticmethod
    def _convert_model_to_location(location: LocationModel) -> Location:
        return Location(
            id=location.id,
            name=location.name,
            description=location.description,
            latitude=location.latitude,
            longitude=location.longitude,
        )
