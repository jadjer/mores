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
from sqlalchemy.orm import selectinload, joinedload

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityUpdateError,
    EntityDeleteError
)
from app.database.models import ServiceModel
from app.database.repositories.base import BaseRepository
from app.models.domain.location import Location
from app.models.domain.service import Service
from app.models.domain.service_type import ServiceType


class ServicesRepository(BaseRepository):

    async def create_service_by_vehicle_id(
            self,
            vehicle_id: int,
            service_type_id: int,
            mileage: int,
            price: float,
            location: Location,
    ) -> Service:
        new_service = ServiceModel()
        new_service.vehicle_id = vehicle_id
        new_service.service_type_id = service_type_id
        new_service.mileage = mileage
        new_service.price = price
        new_service.location.description = location.description
        new_service.location.latitude = location.latitude
        new_service.location.longitude = location.longitude

        self.session.add(new_service)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Service(**new_service.__dict__)

    async def get_services_by_vehicle_id(self, vehicle_id: int) -> List[Service]:
        query = select(ServiceModel).where(ServiceModel.vehicle_id == vehicle_id).options(
            joinedload(ServiceModel.service_type),
            joinedload(ServiceModel.location),
        )
        result = await self.session.execute(query)

        services_in_db = result.scalars().all()

        for service_in_db in services_in_db:
            print("===============================")
            print(service_in_db.__dict__)

        return [self._get_service_from_service_model(service_in_db) for service_in_db in services_in_db]

    async def get_service_by_id_and_vehicle_id(self, service_id: int, vehicle_id: int) -> Service:
        service_in_db = await self._get_service_model_by_id_and_vehicle_id(service_id, vehicle_id)

        return Service(**service_in_db.__dict__)

    async def update_service_by_id_and_vehicle_id(
            self,
            service_id: int,
            vehicle_id: int,
            service_type: Optional[ServiceType] = None,
            mileage: Optional[int] = None,
            price: Optional[float] = None,
            location: Optional[Location] = None,
    ) -> Service:
        service_in_db = await self._get_service_model_by_id_and_vehicle_id(service_id, vehicle_id)
        service_in_db.service_type = service_type or service_in_db.service_type
        service_in_db.mileage = mileage or service_in_db.mileage
        service_in_db.price = price or service_in_db.price

        if location:
            service_in_db.location.description = location.description or service_in_db.location.description
            service_in_db.location.latitude = location.latitude or service_in_db.location.latitude
            service_in_db.location.longitude = location.longitude or service_in_db.location.longitude

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Service(**service_in_db.__dict__)

    async def delete_service_by_id_and_vehicle_id(self, service_id: int, vehicle_id: int) -> None:
        service_in_db = await self._get_service_model_by_id_and_vehicle_id(service_id, vehicle_id)

        try:
            await self.session.delete(service_in_db)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_service_model_by_id_and_vehicle_id(self, service_id: int, vehicle_id: int) -> ServiceModel:
        query = select(ServiceModel).where(
            and_(
                ServiceModel.id == service_id,
                ServiceModel.vehicle_id == vehicle_id
            )
        ).options(selectinload(ServiceModel.location))
        result = await self.session.execute(query)

        service_model_in_db = result.scalars().first()
        if not service_model_in_db:
            raise EntityDoesNotExists

        return service_model_in_db

    @staticmethod
    def _get_service_from_service_model(service_model: ServiceModel) -> Service:
        location = Location(
            description=service_model.location.description,
            latitude=service_model.location.latitude,
            longitude=service_model.location.longitude
        )
        service = Service(
            service_type_name=service_model.service_type.name,
            mileage=service_model.mileage,
            price=service_model.price,
            location=location,
            created_at=service_model.datetime
        )
        return service
