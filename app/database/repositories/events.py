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

from loguru import logger
from datetime import datetime
from typing import (
    List,
    Optional,
)

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityUpdateError,
    EntityDeleteError,
)
from app.database.models import (
    EventModel,
    LocationModel,
)
from app.database.repositories.base import BaseRepository
from app.models.domain.location import Location
from app.models.domain.event import (
    Event,
    EventState,
)
from app.models.domain.user import User


class EventsRepository(BaseRepository):

    async def create_event_by_user_id(
            self,
            user_id: int,
            *,
            title: str,
            body: str,
            started_at: datetime,
            location: Location,
            description: Optional[str] = None,
            thumbnail: Optional[str] = None,
    ) -> Event:
        new_location = LocationModel()
        new_location.description = location.description
        new_location.latitude = location.latitude
        new_location.longitude = location.longitude

        new_event = EventModel()
        new_event.author_id = user_id
        new_event.title = title
        new_event.description = description
        new_event.thumbnail = thumbnail
        new_event.body = body
        new_event.location = new_location
        new_event.started_at = started_at
        new_event.event_state = EventState.PLANNED

        self.session.add(new_event)

        try:
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityCreateError from exception

        return await self.get_event_by_id(new_event.id)

    async def get_event_by_id(self, event_id: int) -> Event:
        event_in_db = await self._get_event_model_by_id(event_id)
        if not event_in_db:
            raise EntityDoesNotExists

        return self._convert_event_model_to_event(event_in_db)

    async def get_event_by_title(self, title: str) -> Event:
        query = select(EventModel).where(
            EventModel.title == title
        ).options(
            joinedload(EventModel.author),
            joinedload(EventModel.location)
        )
        result = await self.session.execute(query)

        event_in_db: EventModel = result.scalars().first()
        if not event_in_db:
            raise EntityDoesNotExists

        return self._convert_event_model_to_event(event_in_db)

    async def get_events_with_filter(
            self,
            state: Optional[EventState] = EventState.PLANNED,
            limit: int = 20,
            offset: int = 0,
    ) -> List[Event]:
        query = select(EventModel).where(EventModel.event_state == state).limit(limit).offset(offset).options(
            joinedload(EventModel.author),
            joinedload(EventModel.location)
        )

        result = await self.session.execute(query)
        events_in_db = result.scalars().all()

        return [self._convert_event_model_to_event(event_in_db) for event_in_db in events_in_db]

    async def update_event_by_id_and_user_id(
            self,
            event_id: int,
            user_id: int,
            *,
            title: Optional[str] = None,
            description: Optional[str] = None,
            thumbnail: Optional[str] = None,
            body: Optional[str] = None,
            started_at: Optional[datetime] = None,
            location: Optional[Location] = None,
            event_state: Optional[EventState] = None,
    ) -> Event:
        event_in_db: EventModel = await self._get_event_model_by_id_and_user_id(event_id, user_id)
        event_in_db.title = title or event_in_db.title
        event_in_db.description = description or event_in_db.description
        event_in_db.thumbnail = thumbnail or event_in_db.thumbnail
        event_in_db.body = body or event_in_db.body
        event_in_db.event_state = event_state or event_in_db.event_state
        event_in_db.started_at = started_at or event_in_db.started_at

        if location:
            event_in_db.location.description = location.description or event_in_db.location.description
            event_in_db.location.latitude = location.latitude or event_in_db.location.latitude
            event_in_db.location.longitude = location.longitude or event_in_db.location.longitude

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return await self.get_event_by_id(event_id)

    async def delete_event_by_id_and_user_id(self, event_id: int, user_id: int) -> None:
        event: EventModel = await self._get_event_model_by_id_and_user_id(event_id, user_id)

        try:
            await self.session.delete(event)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_event_model_by_id(self, event_id: int) -> EventModel:
        query = select(EventModel).where(EventModel.id == event_id).options(
            joinedload(EventModel.author),
            joinedload(EventModel.location)
        )
        result = await self.session.execute(query)

        event_model_in_db: EventModel = result.scalars().first()
        if not event_model_in_db:
            raise EntityDoesNotExists

        return event_model_in_db

    async def _get_event_model_by_id_and_user_id(self, event_id: int, user_id: int) -> EventModel:
        query = select(EventModel).where(
            EventModel.id == event_id,
            EventModel.author_id == user_id
        ).options(
            joinedload(EventModel.author),
            joinedload(EventModel.location)
        )
        result = await self.session.execute(query)

        event_model_in_db: EventModel = result.scalars().first()
        if not event_model_in_db:
            raise EntityDoesNotExists

        return event_model_in_db

    @staticmethod
    def _convert_event_model_to_event(event_model: EventModel) -> Event:
        author = User(**event_model.author.__dict__)
        location = Location(**event_model.location.__dict__)

        event = Event(
            id=event_model.id,
            author=author,
            title=event_model.title,
            description=event_model.description,
            thumbnail=event_model.thumbnail,
            body=event_model.body,
            started_at=event_model.started_at,
            location=location,
            event_state=event_model.event_state,
            created_at=event_model.created_at,
            updated_at=event_model.updated_at,
        )

        return event
