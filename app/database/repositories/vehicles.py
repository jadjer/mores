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
from loguru import logger

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
            *,
            brand: str,
            model: str,
            gen: int,
            year: int,
            color: str,
            mileage: int,
            vin: str,
            registration_plate: str,
            name: str,
    ) -> Vehicle:
        new_vehicle = VehicleModel()
        new_vehicle.owner_id = user_id
        new_vehicle.brand = brand
        new_vehicle.model = model
        new_vehicle.gen = gen
        new_vehicle.year = year
        new_vehicle.color = color
        new_vehicle.mileage = mileage
        new_vehicle.vin = vin
        new_vehicle.registration_plate = registration_plate
        new_vehicle.name = name

        self.session.add(new_vehicle)

        try:
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityCreateError from exception

        return await self.get_vehicle_by_id_and_user_id(new_vehicle.id, user_id)

    async def get_vehicle_by_vin(self, vin: str) -> Vehicle:
        query = select(VehicleModel).where(VehicleModel.vin == vin)
        result = await self.session.execute(query)

        vehicle_in_db: VehicleModel = result.scalars().first()
        if not vehicle_in_db:
            raise EntityDoesNotExists

        return self._convert_vehicle_model_to_vehicle(vehicle_in_db)

    async def get_vehicle_by_registration_plate(self, registration_plate: str) -> Vehicle:
        query = select(VehicleModel).where(VehicleModel.registration_plate == registration_plate)
        result = await self.session.execute(query)

        vehicle_in_db: VehicleModel = result.scalars().first()
        if not vehicle_in_db:
            raise EntityDoesNotExists

        return self._convert_vehicle_model_to_vehicle(vehicle_in_db)

    async def get_vehicle_by_id_and_user_id(self, vehicle_id: int, user_id: int) -> Vehicle:
        vehicle_in_db = await self._get_vehicle_model_by_id_and_user_id(vehicle_id, user_id)
        return self._convert_vehicle_model_to_vehicle(vehicle_in_db)

    async def get_vehicles_by_user_id(self, user_id: int) -> List[Vehicle]:
        query = select(VehicleModel).where(VehicleModel.owner_id == user_id)
        result = await self.session.execute(query)

        vehicles_in_db = result.scalars().all()

        return [self._convert_vehicle_model_to_vehicle(vehicle_in_db) for vehicle_in_db in vehicles_in_db]

    async def update_vehicle_by_id_and_user_id(
            self,
            vehicle_id: int,
            user_id: int,
            *,
            name: Optional[str] = None,
            brand: Optional[str] = None,
            gen: Optional[int] = None,
            model: Optional[str] = None,
            year: Optional[int] = None,
            color: Optional[str] = None,
            mileage: Optional[int] = None,
            vin: Optional[str] = None,
            registration_plate: Optional[str] = None,
    ) -> Vehicle:
        vehicle_in_db = await self._get_vehicle_model_by_id_and_user_id(vehicle_id, user_id)
        vehicle_in_db.brand = brand or vehicle_in_db.brand
        vehicle_in_db.model = model or vehicle_in_db.model
        vehicle_in_db.gen = gen or vehicle_in_db.gen
        vehicle_in_db.year = year or vehicle_in_db.year
        vehicle_in_db.color = color or vehicle_in_db.color
        vehicle_in_db.mileage = mileage or vehicle_in_db.mileage
        vehicle_in_db.vin = vin or vehicle_in_db.vin
        vehicle_in_db.registration_plate = registration_plate or vehicle_in_db.registration_plate
        vehicle_in_db.name = name or vehicle_in_db.name

        try:
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityUpdateError from exception

        return await self.get_vehicle_by_id_and_user_id(vehicle_id, user_id)

    async def delete_vehicle_by_id_and_user_id(self, vehicle_id: int, user_id: int) -> None:
        vehicle_in_db = await self._get_vehicle_model_by_id_and_user_id(vehicle_id, user_id)

        try:
            await self.session.delete(vehicle_in_db)
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityDeleteError from exception

    async def _get_vehicle_model_by_id_and_user_id(self, vehicle_id: int, user_id: int) -> VehicleModel:
        query = select(VehicleModel).where(
            and_(
                VehicleModel.id == vehicle_id,
                VehicleModel.owner_id == user_id,
            )
        )

        result = await self.session.execute(query)

        vehicle_model_in_db: VehicleModel = result.scalars().first()
        if not vehicle_model_in_db:
            raise EntityDoesNotExists

        return vehicle_model_in_db

    @staticmethod
    def _convert_vehicle_model_to_vehicle(vehicle_model: VehicleModel) -> Vehicle:
        return Vehicle(
            id=vehicle_model.id,
            brand=vehicle_model.brand,
            model=vehicle_model.model,
            gen=vehicle_model.gen,
            year=vehicle_model.year,
            color=vehicle_model.color,
            mileage=vehicle_model.mileage,
            vin=vehicle_model.vin,
            registration_plate=vehicle_model.registration_plate,
            name=vehicle_model.name
        )
