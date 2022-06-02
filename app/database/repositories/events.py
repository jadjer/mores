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
from typing import List, Optional

from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from app.database.errors import EntityDoesNotExist, EntityAlreadyExists
from app.database.models import EventModel
from app.database.repositories import UsersRepository
from app.database.repositories.base import BaseRepository
from app.database.repositories.locations import LocationsRepository
from app.database.repositories.posts import PostsRepository
from app.models.domain.location import Location
from app.models.domain.event import Event, EventState
from app.models.domain.user import UserInDB


class EventsRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session)
        self._users_repo: UsersRepository = UsersRepository(session)
        self._posts_repo: PostsRepository = PostsRepository(session)
        self._locations_repo: LocationsRepository = LocationsRepository(session)

    async def get_event_model_by_id(self, event_id: int) -> EventModel:
        query = select(EventModel).where(EventModel.id == event_id)
        result = await self.session.execute(query)

        event_model_in_db: EventModel = result.scalars().first()
        if not event_model_in_db:
            raise EntityDoesNotExist("event with id {} does not exist".format(event_id))

        return event_model_in_db

    async def get_event_by_id(self, event_id: int) -> Event:
        event_model = await self.get_event_model_by_id(event_id)

        user_in_db = await self._users_repo.get_user_by_id(event_model.author_id)
        location_in_db = await self._locations_repo.get_location(event_model.location_id)

        return Event(**event_model.__dict__)

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
        location_in_db = await self._locations_repo.create_location(
            name=location.name,
            description=location.description,
            latitude=location.latitude,
            longitude=location.longitude,
        )

        post_in_db = await self._posts_repo.create_post(
            author=author,
            title=title,
            description=description,
            thumbnail=thumbnail,
            body=body,
        )

        new_event = EventModel()
        new_event.post_id = post_in_db.id
        new_event.location_id = location_in_db.id
        new_event.started_at = started_at
        new_event.event_state = EventState.PLANNED

        try:
            self.session.add(new_event)
            await self.session.commit()

        except Exception:
            raise EntityAlreadyExists("Conflict vin or registration plate")

        return Event(**new_event.__dict__)

    async def update_event(
            self,
            *,
            user: UserInDB,
            event_id: int,
            title: str,
            description: str,
            thumbnail: str,
            body: str,
            started_at: datetime,
            location: Location,
            event_state: EventState,
    ) -> Event:
        query = update(EventModel).where(EventModel.id == event_id).values(
            title=title,
            description=description,
            thumbnail=thumbnail,
            body=body,
            started_at=started_at,
            location_id=location.id,
            event_state=event_state
        )
        result = self.session.execute(query)

        event_in_db: EventModel = result.scalars().first()
        if not event_in_db:
            raise EntityDoesNotExist("event with id {0} does not exist".format(event_id))

        return self._convert_model_to_event(user, location, event_in_db)

    async def delete_event(self, event_id: int) -> None:
        query = delete(EventModel).where(EventModel.id == event_id)
        await self.session.execute(query)
        await self.session.commit()

    async def filter_events(
            self,
            author: Optional[str] = None,
            state: Optional[EventState] = EventState.PLANNED,
            limit: int = 20,
            offset: int = 0,
    ) -> List[Event]:
        events: List[Event] = []

        query = select(EventModel)

        if author:
            user = await self._users_repo.get_user_by_username(author)
            query = query.where(EventModel.author_id == user.id)

        query = query.where(EventModel.event_state == state)
        query = query.limit(limit)
        query = query.offset(offset)

        result = await self.session.execute(query)
        events_in_db = result.scalars().all()

        for event in events_in_db:
            author = await self._users_repo.get_user_by_id(event.author_id)
            location = await self._locations_repo.get_location(event.location_id)

            events.append(Event(**event.__dict__, author=author, location=location))

        return events
