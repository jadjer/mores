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

from fastapi import APIRouter, Depends

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.events import (
    get_event_id_from_path,
    get_event_confirmation_from_query
)
from app.models.domain.event import EventState
from app.models.domain.user import UserInDB

router = APIRouter()


@router.post(
    "",
    name="events:confirmation",
)
async def confirmation(
        event_id: int = Depends(get_event_id_from_path),
        event_confirmation: EventState = Depends(get_event_confirmation_from_query),
        user: UserInDB = Depends(get_current_user_authorizer(required=True)),
) -> None:
    pass
