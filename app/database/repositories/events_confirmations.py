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

from sqlalchemy import select, update, insert

from app.database.errors import EntityDoesNotExist
from app.database.models import EventConfirmationModel
from app.database.repositories.base import BaseRepository
from app.models.domain.event_confirmation import EventConfirmation, EventConfirmationType
from app.models.domain.event import Event
from app.models.domain.user import UserInDB


class EventConfirmationsRepository(BaseRepository):

    async def get_confirmation_by_event_id_for_user(self, event: Event, user: UserInDB) -> EventConfirmation:
        query = select(
            EventConfirmationModel
        ).where(
            EventConfirmationModel.event_id == event.id
        ).where(
            EventConfirmationModel.user_id == user.id
        )

        result = await self.session.execute(query)
        event_confirmation_in_db: EventConfirmationModel = result.scalars().first()

        if not event_confirmation_in_db:
            raise EntityDoesNotExist("event confirmation with event id {0} does not exist".format(event.id))

        return EventConfirmation(
            event=event,
            user=user,
            type=event_confirmation_in_db.confirmation_type
        )

    async def create_confirmation_by_event_id_for_user(
            self,
            event: Event,
            user: UserInDB,
            event_confirmation: EventConfirmationType
    ) -> EventConfirmation:
        query = insert(
            EventConfirmationModel
        ).values(
            event_id=event.id,
            user_id=user.id,
            confirmation_type=event_confirmation
        )

        await self.session.execute(query)
        await self.session.commit()

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
