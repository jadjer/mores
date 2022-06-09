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

from typing import List, Optional
from datetime import date

from sqlalchemy import (
    select,
    and_,
)
from sqlalchemy.orm import selectinload

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityUpdateError,
    EntityDeleteError
)
from app.database.models import (
    ReminderModel
)
from app.database.repositories.base import BaseRepository
from app.models.domain.reminder import Reminder


class RemindersRepository(BaseRepository):

    async def create_reminder_by_vehicle_id(
            self,
            vehicle_id: int,
            service_type_id: int,
            next_mileage: int,
            next_date: date,
    ) -> Reminder:
        new_reminder = ReminderModel()
        new_reminder.vehicle_id = vehicle_id
        new_reminder.service_type_id = service_type_id
        new_reminder.next_mileage = next_mileage
        new_reminder.next_data = next_date

        self.session.add(new_reminder)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Reminder(**new_reminder.__dict__)

    async def get_reminders_by_vehicle_id(self, vehicle_id: int) -> List[Reminder]:
        query = select(ReminderModel).where(
            ReminderModel.vehicle_id == vehicle_id
        ).options(
            selectinload(ReminderModel.vehicle),
            selectinload(ReminderModel.service_type)
        )
        result = await self.session.execute(query)

        reminders_in_db = result.scalars().all()

        for reminder_in_db in reminders_in_db:
            print("=========================================")
            print(reminder_in_db.__dict__)

        return [Reminder(**reminder_in_db.__dict__) for reminder_in_db in reminders_in_db]

    async def get_reminder_by_id_and_vehicle_id(self, reminder_id: int, vehicle_id: int) -> Reminder:
        reminder_in_db = await self._get_reminder_model_by_id_and_vehicle_id(reminder_id, vehicle_id)

        return Reminder(**reminder_in_db.__dict__)

    async def update_reminder_by_id_and_vehicle_id(
            self,
            reminder_id: int,
            vehicle_id: int,
            service_type_id: Optional[int] = None,
            next_mileage: Optional[int] = None,
            next_date: Optional[date] = None,
    ) -> Reminder:
        reminder_in_db = await self._get_reminder_model_by_id_and_vehicle_id(reminder_id, vehicle_id)
        reminder_in_db.service_type_id = service_type_id or reminder_in_db.service_type_id
        reminder_in_db.next_mileage = next_mileage or reminder_in_db.next_mileage
        reminder_in_db.next_date = next_date or reminder_in_db.next_data

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Reminder(**reminder_in_db.__dict__)

    async def delete_reminder_by_id_and_vehicle_id(self, reminder_id: int, vehicle_id: int) -> None:
        reminder_in_db = await self._get_reminder_model_by_id_and_vehicle_id(reminder_id, vehicle_id)

        try:
            await self.session.delete(reminder_in_db)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_reminder_model_by_id_and_vehicle_id(self, reminder_id: int, vehicle_id: int) -> ReminderModel:
        query = select(ReminderModel).where(
            and_(
                ReminderModel.id == reminder_id,
                ReminderModel.vehicle_id == vehicle_id
            )
        ).options(
            selectinload(ReminderModel.vehicle),
            selectinload(ReminderModel.service_type)
        )
        result = await self.session.execute(query)

        reminder_model_in_db = result.scalars().first()
        if not reminder_model_in_db:
            raise EntityDoesNotExists

        return reminder_model_in_db
