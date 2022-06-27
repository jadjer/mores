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

from loguru import logger
from sqlalchemy.future import select

from app.database.models import ApiKeyModel
from app.database.repositories.base import BaseRepository


class ApiKeysRepository(BaseRepository):

    async def is_exists_key(self, key: str) -> bool:
        query = select(ApiKeyModel).where(ApiKeyModel.key == key)
        result = await self.session.execute(query)

        key_in_db: ApiKeyModel = result.scalars().first()
        if not key_in_db:
            logger.error("API Key {} not found".format(key))
            return False

        if key_in_db.is_revoked is True:
            logger.error("API Key for {} is revoked".format(key_in_db.description))
            return False

        return True
