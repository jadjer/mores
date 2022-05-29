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

from datetime import datetime

from sqlalchemy import select, DateTime, cast
from sqlalchemy.orm import Session

from app.database.errors import EntityDoesNotExist
from app.database.models import EventModel
from app.database.repositories.base import BaseRepository
from app.database.repositories.locations import LocationsRepository
from app.models.domain.location import Location
from app.models.domain.event import Event, EventState
from app.models.domain.user import User, UserInDB


class EventsRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session)
        self._locations_repo: LocationsRepository = LocationsRepository(session)

    async def create_event(
            self,
            *,
            author: UserInDB,
            title: str,
            description: str,
            thumbnail: str,
            body: str,
            started_at: datetime,
            location: Location,
    ) -> Event:
        location_id = await self._locations_repo.create_location(
            name=location.name,
            description=location.description,
            latitude=location.latitude,
            longitude=location.longitude,
        )

        event = EventModel(
            author_id=author.id,
            title=title,
            description=description,
            thumbnail=thumbnail,
            body=body,
            started_at=started_at.replace(tzinfo=None),
            location_id=location_id,
            event_state=EventState.PLANNED,
        )

        self.session.add(event)
        await self.session.commit()
        self.session.refresh(event)

        return Event(**event.__dict__, author=author, location=location)

    async def _get_event_from_db(self, event_id: int) -> Event:
        query = select(EventModel).where(EventModel.id == event_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            return Event(**user.__dict__)

        raise EntityDoesNotExist("event with id {0} does not exist".format(event_id))
