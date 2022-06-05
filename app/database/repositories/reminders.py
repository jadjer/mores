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

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityUpdateError,
    EntityDeleteError
)
from app.database.models import (
    LocationModel,
    ReminderModel
)
from app.database.repositories.base import BaseRepository
from app.database.repositories.locations import LocationsRepository
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.location import Location
from app.models.domain.reminder import Reminder
from app.models.domain.service_type import ServiceType


class RemindersRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session)
        self._vehicles_repo = VehiclesRepository(session)
        self._locations_repo = LocationsRepository(session)

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
        query = select(ReminderModel).where(ReminderModel.vehicle_id == vehicle_id)
        result = await self.session.execute(query)

        reminders_in_db = result.scalars().all()

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

        self.session.delete(reminder_in_db)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_reminder_model_by_id_and_vehicle_id(self, reminder_id: int, vehicle_id: int) -> ReminderModel:
        query = select(ReminderModel).where(
            and_(
                ReminderModel.id == reminder_id,
                ReminderModel.vehicle_id == vehicle_id
            )
        ).options(selectinload(ReminderModel.location))
        result = await self.session.execute(query)

        reminder_model_in_db = result.scalars().first()
        if not reminder_model_in_db:
            raise EntityDoesNotExists

        return reminder_model_in_db
