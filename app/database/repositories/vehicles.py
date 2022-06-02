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

from sqlalchemy import select

from app.database.errors import EntityDoesNotExist
from app.database.errors.vehicle_already_exist import VehicleAlreadyExist
from app.database.models import VehicleModel
from app.database.repositories.base import BaseRepository
from app.models.domain.user import UserInDB
from app.models.domain.vehicle import Vehicle


class VehiclesRepository(BaseRepository):

    async def get_vehicle_by_vin(self, vin: str) -> Vehicle:
        query = select(VehicleModel).where(VehicleModel.vin == vin)
        result = await self.session.execute(query)

        vehicle_in_db: VehicleModel = result.scalars().first()
        if not vehicle_in_db:
            raise EntityDoesNotExist("vehicle with vin {} does not exist".format(vin))

        return Vehicle(**vehicle_in_db.__dict__)

    async def get_vehicle_by_registration_plate(self, registration_plate: str) -> Vehicle:
        query = select(VehicleModel).where(VehicleModel.registration_plate == registration_plate)
        result = await self.session.execute(query)

        vehicle_in_db: VehicleModel = result.scalars().first()
        if not vehicle_in_db:
            raise EntityDoesNotExist("vehicle with registration plate {} does not exist".format(registration_plate))

        return Vehicle(**vehicle_in_db.__dict__)

    async def get_vehicle_model_by_id(self, user: UserInDB, vehicle_id: int) -> VehicleModel:
        query = select(VehicleModel).where(VehicleModel.owner_id == user.id).where(VehicleModel.id == vehicle_id)
        result = await self.session.execute(query)

        vehicle_model_in_db: VehicleModel = result.scalars().first()
        if not vehicle_model_in_db:
            raise EntityDoesNotExist("vehicle with id {} does not exist".format(vehicle_id))

        return vehicle_model_in_db

    async def get_vehicle_by_id(self, user: UserInDB, vehicle_id: int) -> Vehicle:
        vehicle_model = await self.get_vehicle_model_by_id(user, vehicle_id)
        return Vehicle(**vehicle_model.__dict__)

    async def get_vehicles(self, user: UserInDB) -> List[Vehicle]:
        query = select(VehicleModel).where(VehicleModel.owner_id == user.id)
        result = await self.session.execute(query)

        vehicles_in_db = result.scalars().all()

        return [Vehicle(**vehicle_in_db.__dict__) for vehicle_in_db in vehicles_in_db]

    async def create_vehicle(
            self,
            user: UserInDB,
            *,
            brand: str,
            model: str,
            year: int,
            color: str,
            mileage: int,
            vin: str,
            registration_plate: str,
    ) -> Vehicle:
        new_vehicle = VehicleModel()
        new_vehicle.owner_id = user.id
        new_vehicle.brand = brand
        new_vehicle.model = model
        new_vehicle.year = year
        new_vehicle.color = color
        new_vehicle.mileage = mileage
        new_vehicle.vin = vin
        new_vehicle.registration_plate = registration_plate

        try:
            self.session.add(new_vehicle)
            await self.session.commit()

        except Exception:
            raise VehicleAlreadyExist("Conflict vin or registration plate")

        return Vehicle(**new_vehicle.__dict__)

    async def update_vehicle(
            self,
            user: UserInDB,
            vehicle_id: int,
            *,
            brand: Optional[str],
            model: Optional[str],
            year: Optional[int],
            color: Optional[str],
            mileage: Optional[int],
            vin: Optional[str],
            registration_plate: Optional[str],
    ) -> Vehicle:
        vehicle = await self.get_vehicle_model_by_id(user, vehicle_id)
        vehicle.brand = brand or vehicle.brand
        vehicle.model = model or vehicle.model
        vehicle.year = year or vehicle.year
        vehicle.color = color or vehicle.color
        vehicle.mileage = mileage or vehicle.mileage
        vehicle.vin = vin or vehicle.vin
        vehicle.registration_plate = registration_plate or vehicle.registration_plate

        try:
            await self.session.commit()

        except Exception:
            raise VehicleAlreadyExist("Conflict vin or registration plate")

        return Vehicle(**vehicle.__dict__)

    async def delete_vehicle(self, user: UserInDB, vehicle_id: int) -> None:
        vehicle = await self.get_vehicle_model_by_id(user, vehicle_id)

        await self.session.delete(vehicle)
        await self.session.commit()
