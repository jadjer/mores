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

from typing import List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.database.errors import EntityDoesNotExists, EntityCreateError
from app.database.models import ServiceModel
from app.database.repositories.base import BaseRepository
from app.database.repositories.locations import LocationsRepository
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.service import Service
from app.models.domain.user import UserInDB
from app.services.vehicles import check_user_is_owner


class ServicesRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session)
        self._vehicles_repo = VehiclesRepository(session)
        self._locations_repo = LocationsRepository(session)

    async def create_service(
            self,
            vehicle_id: int,
    ) -> Service:
        new_service = ServiceModel()
        new_service.vehicle_id = vehicle_id

        self.session.add(new_service)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Service(**new_service.__dict__)

    async def get_service_model_by_id(self, service_id: int) -> ServiceModel:
        query = select(ServiceModel).where(ServiceModel.id == service_id)
        result = await self.session.execute(query)

        service_model_in_db: ServiceModel = result.scalars().first()
        if not service_model_in_db:
            raise EntityDoesNotExists

        return service_model_in_db

    async def get_service_by_id(self, user: UserInDB, service_id: int) -> Service:
        service_model = await self.get_service_model_by_id(service_id)

        vehicle = await self._vehicles_repo.get_vehicle_by_id(user, service_model.vehicle_id)
        location = await self._locations_repo.get_location_by_id(service_model.location_id)

        return Service(vehicle=vehicle, location=location, **service_model.__dict__)

    async def get_services_for_vehicle(self, user: UserInDB, vehicle_id: int) -> List[Service]:
        if not check_user_is_owner(self._vehicles_repo, user, vehicle_id):
            raise EntityDoesNotExists

        query = select(ServiceModel).where(ServiceModel.vehicle_id == vehicle_id)
        result = await self.session.execute(query)

        services_in_db = result.scalars().all()

        return [Service(**service_in_db.__dict__) for service_in_db in services_in_db]

