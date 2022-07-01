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

from loguru import logger
from sqlalchemy.future import select

from app.database.errors import EntityCreateError, EntityDoesNotExists
from app.database.models import ApiKeyModel
from app.database.repositories.base import BaseRepository
from app.models.domain.api_key import ApiKey
from app.services.security import generate_salt


class ApiKeysRepository(BaseRepository):

    async def create_key(self, description: str) -> ApiKey:
        new_key = ApiKeyModel()
        new_key.description = description
        new_key.key = generate_salt()
        new_key.is_revoked = False

        self.session.add(new_key)

        try:
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityCreateError from exception

        return await self.get_key_by_id(new_key.id)

    async def get_key_by_id(self, key_id: int) -> ApiKey:
        key_in_db: ApiKeyModel = await self._get_key_model_by_id(key_id)
        if not key_in_db:
            logger.error("API Key with id {} not found".format(key_id))
            raise EntityDoesNotExists

        return self._convert_key_model_to_key(key_in_db)

    async def is_exists_key(self, key: str) -> bool:
        key_in_db: ApiKeyModel = await self._get_key_model_by_key(key)
        if not key_in_db:
            logger.error("API Key {} not found".format(key))
            return False

        if key_in_db.is_revoked is True:
            logger.error("API Key for {} is revoked".format(key_in_db.description))
            return False

        return True

    async def get_keys(self) -> List[ApiKey]:
        query = select(ApiKeyModel)
        result = await self.session.execute(query)

        keys_in_db: List[ApiKeyModel] = result.scalars().all()
        key_in_db: ApiKeyModel

        return [self._convert_key_model_to_key(key_in_db) for key_in_db in keys_in_db]

    async def mark_key_as_revoked(self, key_id: int) -> ApiKey:
        key_in_db: ApiKeyModel = await self._get_key_model_by_id(key_id)
        if not key_in_db:
            logger.error("API Key with id {} not found".format(key_id))
            raise EntityDoesNotExists

        key_in_db.is_revoked = True

        return self._convert_key_model_to_key(key_in_db)

    async def _get_key_model_by_id(self, key_id: int) -> ApiKeyModel:
        query = select(ApiKeyModel).where(ApiKeyModel.id == key_id)
        result = await self.session.execute(query)

        key_in_db: ApiKeyModel = result.scalars().first()
        if not key_in_db:
            logger.error("API Key with id {} not found".format(key_id))
            raise EntityDoesNotExists

        return key_in_db

    async def _get_key_model_by_key(self, key: str) -> ApiKeyModel:
        query = select(ApiKeyModel).where(ApiKeyModel.key == key)
        result = await self.session.execute(query)

        key_in_db: ApiKeyModel = result.scalars().first()
        if not key_in_db:
            logger.error("API Key {} not found".format(key))
            raise EntityDoesNotExists

        return key_in_db

    @staticmethod
    def _convert_key_model_to_key(key: ApiKeyModel) -> ApiKey:
        return ApiKey(
            id=key.id,
            key=key.key,
            description=key.description,
            is_revoked=key.is_revoked,
            created_at=key.created_at,
            updated_at=key.updated_at,
        )
