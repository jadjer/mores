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
from datetime import datetime

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
    FuelModel
)
from app.database.repositories.base import BaseRepository
from app.database.repositories.locations import LocationsRepository
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.location import Location
from app.models.domain.fuel import Fuel, FuelType


class FuelsRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session)
        self._vehicles_repo = VehiclesRepository(session)
        self._locations_repo = LocationsRepository(session)

    async def create_fuel_by_vehicle_id(
            self,
            vehicle_id: int,
            quantity: float,
            price: float,
            mileage: int,
            fuel_type: FuelType,
            location: Location,
            is_full: bool,
    ) -> Fuel:
        new_fuel = FuelModel()
        new_fuel.vehicle_id = vehicle_id
        new_fuel.quantity = quantity
        new_fuel.price = price
        new_fuel.mileage = mileage
        new_fuel.fuel_type = fuel_type
        new_fuel.location = LocationModel(**location.__dict__)
        new_fuel.is_full = is_full
        new_fuel.datetime = datetime.now()

        self.session.add(new_fuel)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Fuel(**new_fuel.__dict__)

    async def get_fuels_by_vehicle_id(self, vehicle_id: int) -> List[Fuel]:
        query = select(FuelModel).where(FuelModel.vehicle_id == vehicle_id)
        result = await self.session.execute(query)

        fuels_in_db = result.scalars().all()

        return [Fuel(**fuel_in_db.__dict__) for fuel_in_db in fuels_in_db]

    async def get_fuel_by_id_and_vehicle_id(self, fuel_id: int, vehicle_id: int) -> Fuel:
        fuel_in_db = await self._get_fuel_model_by_id_and_vehicle_id(fuel_id, vehicle_id)

        return Fuel(**fuel_in_db.__dict__)

    async def update_fuel_by_id_and_vehicle_id(
            self,
            fuel_id: int,
            vehicle_id: int,
            quantity: Optional[float] = None,
            price: Optional[float] = None,
            mileage: Optional[str] = None,
            fuel_type: Optional[FuelType] = None,
            location: Optional[Location] = None,
            is_full: Optional[bool] = None,
    ) -> Fuel:
        fuel_in_db = await self._get_fuel_model_by_id_and_vehicle_id(fuel_id, vehicle_id)
        fuel_in_db.quantity = quantity or fuel_in_db.quantity
        fuel_in_db.price = price or fuel_in_db.price
        fuel_in_db.mileage = mileage or fuel_in_db.mileage
        fuel_in_db.fuel_type = fuel_type or fuel_in_db.fuel_type
        fuel_in_db.location = LocationModel(**location.__dict__) or fuel_in_db.location
        fuel_in_db.is_full = is_full or fuel_in_db.is_full

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Fuel(**fuel_in_db.__dict__)

    async def delete_fuel_by_id_and_vehicle_id(self, fuel_id: int, vehicle_id: int) -> None:
        fuel_in_db = await self._get_fuel_model_by_id_and_vehicle_id(fuel_id, vehicle_id)

        self.session.delete(fuel_in_db)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_fuel_model_by_id_and_vehicle_id(self, fuel_id: int, vehicle_id: int) -> FuelModel:
        query = select(FuelModel).where(
            and_(
                FuelModel.id == fuel_id,
                FuelModel.vehicle_id == vehicle_id
            )
        ).options(selectinload(FuelModel.location))
        result = await self.session.execute(query)

        fuel_model_in_db = result.scalars().first()
        if not fuel_model_in_db:
            raise EntityDoesNotExists

        return fuel_model_in_db
