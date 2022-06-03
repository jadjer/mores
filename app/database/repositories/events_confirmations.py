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

from sqlalchemy import select, update, insert, and_
from sqlalchemy.orm import Session

from app.database.errors import EntityDoesNotExists, EntityCreateError
from app.database.models import EventConfirmationModel
from app.database.repositories.base import BaseRepository
from app.database.repositories.events import EventsRepository
from app.database.repositories.profiles import ProfilesRepository
from app.models.domain.event_confirmation import EventConfirmation, EventConfirmationType
from app.models.domain.event import Event
from app.models.domain.user import UserInDB


class EventConfirmationsRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session)
        self._events_repo = EventsRepository(session)
        self._profiles_repo = ProfilesRepository(session)

    async def get_confirmation_by_event_id_for_user(self, event_id: int, user_id: int) -> EventConfirmation:
        event_confirmation_in_db = await self._get_event_confirmation_mode_by_event_id(event_id, user_id)

        event_in_db = await self._events_repo.get_event_by_id(event_id)
        profile_in_db = await self._profiles_repo.get_profile_by_user_id(user_id)

        return EventConfirmation(
            event=event_in_db,
            user=profile_in_db,
            type=event_confirmation_in_db.confirmation_type
        )

    async def create_confirmation_by_event_id_for_user(
            self,
            event_id: int,
            user_id: int,
            event_confirmation: EventConfirmationType
    ) -> EventConfirmation:
        new_event_confirmation = EventConfirmationModel()
        new_event_confirmation.event_id = event_id
        new_event_confirmation.user_id = user_id
        new_event_confirmation.confirmation_type = event_confirmation

        self.session.add(new_event_confirmation)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return EventConfirmation(
            event=event,
            user=user,
            type=event_confirmation
        )

    async def update_confirmation_by_event_id_for_user(
            self,
            event: Event,
            user: UserInDB,
            event_confirmation: EventConfirmationType
    ) -> EventConfirmation:
        query = update(
            EventConfirmationModel
        ).where(
            EventConfirmationModel.event_id == event.id
        ).where(
            EventConfirmationModel.user_id == user.id
        ).values(
            confirmation_type=event_confirmation
        )

        await self.session.execute(query)
        await self.session.commit()

        return EventConfirmation(
            event=event,
            user=user,
            type=event_confirmation
        )

    async def _get_event_confirmation_mode_by_event_id(self, event_id: int, user_id: int) -> EventConfirmationModel:
        query = select(EventConfirmationModel).where(
            and_(
                EventConfirmationModel.event_id == event_id,
                EventConfirmationModel.user_id == user_id,
            )
        )
        result = await self.session.execute(query)

        event_confirmation_in_db = result.scalars().first()
        if not event_confirmation_in_db:
            raise EntityDoesNotExists

        return event_confirmation_in_db
