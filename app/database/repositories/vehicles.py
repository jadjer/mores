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
from sqlalchemy import select, and_
from sqlalchemy.exc import PendingRollbackError

from app.database.errors import (
    EntityDoesNotExists,
    EntityDeleteError,
    EntityUpdateError,
    EntityCreateError,
)
from app.database.models import VehicleModel
from app.database.repositories.base import BaseRepository
from app.models.domain.vehicle import Vehicle


class VehiclesRepository(BaseRepository):

    async def create_vehicle_by_user_id(
            self,
            user_id: int,
            name: str,
            brand: str,
            model: str,
            year: int,
            color: str,
            mileage: int,
            vin: str,
            registration_plate: str,
    ) -> Vehicle:
        new_vehicle = VehicleModel()
        new_vehicle.owner_id = user_id
        new_vehicle.name = name
        new_vehicle.brand = brand
        new_vehicle.model = model
        new_vehicle.year = year
        new_vehicle.color = color
        new_vehicle.mileage = mileage
        new_vehicle.vin = vin
        new_vehicle.registration_plate = registration_plate

        self.session.add(new_vehicle)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Vehicle(**new_vehicle.__dict__)

    async def get_vehicle_by_vin(self, vin: str) -> Vehicle:
        query = select(VehicleModel).where(VehicleModel.vin == vin)
        result = await self.session.execute(query)

        vehicle_in_db: VehicleModel = result.scalars().first()
        if not vehicle_in_db:
            raise EntityDoesNotExists

        return Vehicle(**vehicle_in_db.__dict__)

    async def get_vehicle_by_registration_plate(self, registration_plate: str) -> Vehicle:
        query = select(VehicleModel).where(VehicleModel.registration_plate == registration_plate)
        result = await self.session.execute(query)

        vehicle_in_db: VehicleModel = result.scalars().first()
        if not vehicle_in_db:
            raise EntityDoesNotExists

        return Vehicle(**vehicle_in_db.__dict__)

    async def get_vehicle_by_id_and_user_id(self, vehicle_id: int, user_id: int) -> Vehicle:
        vehicle_in_db = await self._get_vehicle_model_by_id_and_user_id(vehicle_id, user_id)
        return Vehicle(**vehicle_in_db.__dict__)

    async def get_vehicles_by_user_id(self, user_id: int) -> List[Vehicle]:
        query = select(VehicleModel).where(VehicleModel.owner_id == user_id)
        result = await self.session.execute(query)

        vehicles_in_db = result.scalars().all()

        return [Vehicle(**vehicle_in_db.__dict__) for vehicle_in_db in vehicles_in_db]

    async def update_vehicle_by_id_and_user_id(
            self,
            vehicle_id: int,
            user_id: int,
            name: Optional[str] = None,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            year: Optional[int] = None,
            color: Optional[str] = None,
            mileage: Optional[int] = None,
            vin: Optional[str] = None,
            registration_plate: Optional[str] = None,
    ) -> Vehicle:
        vehicle_in_db = await self._get_vehicle_model_by_id_and_user_id(vehicle_id, user_id)
        vehicle_in_db.name = name or vehicle_in_db.name
        vehicle_in_db.brand = brand or vehicle_in_db.brand
        vehicle_in_db.model = model or vehicle_in_db.model
        vehicle_in_db.year = year or vehicle_in_db.year
        vehicle_in_db.color = color or vehicle_in_db.color
        vehicle_in_db.mileage = mileage or vehicle_in_db.mileage
        vehicle_in_db.vin = vin or vehicle_in_db.vin
        vehicle_in_db.registration_plate = registration_plate or vehicle_in_db.registration_plate

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Vehicle(**vehicle_in_db.__dict__)

    async def delete_vehicle_by_id_and_user_id(self, vehicle_id: int, user_id: int) -> None:
        vehicle_in_db = await self._get_vehicle_model_by_id_and_user_id(vehicle_id, user_id)

        try:
            await self.session.delete(vehicle_in_db)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_vehicle_model_by_id_and_user_id(self, vehicle_id: int, user_id: int) -> VehicleModel:
        query = select(VehicleModel).where(
            and_(
                VehicleModel.id == vehicle_id,
                VehicleModel.owner_id == user_id,
            )
        )

        try:
            result = await self.session.execute(query)
        except PendingRollbackError:
            await self.session.rollback()
            result = await self.session.execute(query)

        vehicle_model_in_db: VehicleModel = result.scalars().first()
        if not vehicle_model_in_db:
            raise EntityDoesNotExists

        return vehicle_model_in_db
