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

from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityUpdateError,
)
from app.database.models import EventConfirmationModel
from app.database.repositories.base import BaseRepository
from app.models.domain.event_confirmation import (
    EventConfirmation,
    EventConfirmationType,
)


class EventConfirmationsRepository(BaseRepository):

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

        return EventConfirmation(**new_event_confirmation.__dict__)

    async def get_confirmation_by_event_id_and_user_id(self, event_id: int, user_id: int) -> EventConfirmation:
        event_confirmation_in_db = await self._get_confirmation_model_by_event_id_and_user_id(event_id, user_id)

        return EventConfirmation(**event_confirmation_in_db.__dict__)

    async def update_confirmation_by_event_id_and_user_id(
            self,
            event_id: int,
            user_id: int,
            event_confirmation: Optional[EventConfirmationType] = None
    ) -> EventConfirmation:
        event_confirmation_in_db = await self._get_confirmation_model_by_event_id_and_user_id(event_id, user_id)
        event_confirmation_in_db.event_confirmation = event_confirmation or event_confirmation_in_db.event_confirmation

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return EventConfirmation(**event_confirmation_in_db.__dict__)

    async def _get_confirmation_model_by_event_id_and_user_id(
            self,
            event_id: int,
            user_id: int
    ) -> EventConfirmationModel:
        query = select(EventConfirmationModel).where(
            and_(
                EventConfirmationModel.event_id == event_id,
                EventConfirmationModel.user_id == user_id,
            )
        ).options(
            joinedload(EventConfirmationModel.event),
            joinedload(EventConfirmationModel.user)
        )
        result = await self.session.execute(query)

        event_confirmation_in_db = result.scalars().first()
        if not event_confirmation_in_db:
            raise EntityDoesNotExists

        return event_confirmation_in_db
