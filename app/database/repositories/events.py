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

from datetime import datetime
from typing import (
    List,
    Optional,
)

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityUpdateError,
    EntityDeleteError,
)
from app.database.models import (
    EventModel,
    PostModel,
    LocationModel,
)
from app.database.repositories.base import BaseRepository
from app.database.repositories.profiles import ProfilesRepository
from app.models.domain.location import Location
from app.models.domain.event import (
    Event,
    EventState,
)


class EventsRepository(BaseRepository):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._profiles_repo = ProfilesRepository(session)

    async def create_event_by_user_id(
            self,
            user_id: int,
            title: str,
            body: str,
            started_at: datetime,
            location: Location,
            description: Optional[str] = None,
            thumbnail: Optional[str] = None,
    ) -> Event:
        new_event = EventModel()
        new_event.post = PostModel(
            author_id=user_id,
            title=title,
            description=description,
            thumbnail=thumbnail,
            body=body
        )
        new_event.location = LocationModel(**location.__dict__)
        new_event.started_at = started_at
        new_event.event_state = EventState.PLANNED

        self.session.add(new_event)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Event(**new_event.__dict__)

    async def get_events_with_filter(
            self,
            author: Optional[str] = None,
            state: Optional[EventState] = EventState.PLANNED,
            limit: int = 20,
            offset: int = 0,
    ) -> List[Event]:
        query = select(EventModel)

        if author:
            profile = await self._profiles_repo.get_profile_by_username(author)
            query = query.where(EventModel.post.author_id == profile.user_id)

        query = query.where(EventModel.event_state == state)
        query = query.limit(limit)
        query = query.offset(offset)
        query = query.options(
            joinedload(EventModel.post),
            joinedload(EventModel.location)
        )

        result = await self.session.execute(query)
        events_in_db = result.scalars().all()

        return [Event(**event_in_db.__dict__, ) for event_in_db in events_in_db]

    async def get_event_by_id(self, event_id: int) -> Event:
        event_in_db = self.session.get(EventModel, event_id)

        if not event_in_db:
            raise EntityDoesNotExists

        return Event(**event_in_db.__dict__)

    async def get_event_by_title(self, title: str) -> Event:
        query = select(EventModel).where(
            EventModel.post.title == title
        ).options(
            joinedload(EventModel.post),
            joinedload(EventModel.location)
        )
        result = await self.session.execute(query)

        event_in_db: EventModel = result.scalars().first()
        if not event_in_db:
            raise EntityDoesNotExists

        return Event(**event_in_db.__dict__)

    async def update_event_by_id_and_user_id(
            self,
            event_id: int,
            user_id: int,
            title: Optional[str] = None,
            description: Optional[str] = None,
            thumbnail: Optional[str] = None,
            body: Optional[str] = None,
            started_at: Optional[datetime] = None,
            location: Optional[Location] = None,
            event_state: Optional[EventState] = None,
    ) -> Event:
        event_in_db: EventModel = await self._get_event_model_by_id_and_user_id(event_id, user_id)
        event_in_db.event_state = event_state or event_in_db.event_state
        event_in_db.started_at = started_at or event_in_db.started_at
        event_in_db.post.title = title or event_in_db.post.title
        event_in_db.post.description = description or event_in_db.post.description
        event_in_db.post.thumbnail = thumbnail or event_in_db.post.thumbnail
        event_in_db.post.body = body or event_in_db.post.body
        event_in_db.location.description = location.description or event_in_db.location.description
        event_in_db.location.latitude = location.latitude or event_in_db.location.latitude
        event_in_db.location.longitude = location.longitude or event_in_db.location.longitude

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Event(**event_in_db.__dict__)

    async def delete_event_by_id_and_user_id(self, event_id: int, user_id: int) -> None:
        event: EventModel = await self._get_event_model_by_id_and_user_id(event_id, user_id)

        try:
            await self.session.delete(event)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_event_model_by_id_and_user_id(self, event_id: int, user_id: int) -> EventModel:
        query = select(EventModel).where(
            EventModel.id == event_id,
            EventModel.post.author.id == user_id
        ).options(
            joinedload(EventModel.post),
            joinedload(EventModel.location)
        )
        result = await self.session.execute(query)

        event_model_in_db: EventModel = result.scalars().first()
        if not event_model_in_db:
            raise EntityDoesNotExists

        return event_model_in_db
