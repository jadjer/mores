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
from typing import Optional

from fastapi import APIRouter, status, Depends, Body

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.events import get_events_filters
from app.database.repositories.events import EventsRepository
from app.models.domain.user import User, UserInDB
from app.models.schemas.events import EventsFilters, ListOfEventsInResponse, EventInResponse, EventInCreate

router = APIRouter()


@router.get(
    "",
    response_model=ListOfEventsInResponse,
    name="events:get-actual-events",
)
async def get_events(
        events_filters: EventsFilters = Depends(get_events_filters),
        user: Optional[User] = Depends(get_current_user_authorizer(required=False)),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> ListOfEventsInResponse:
    pass


@router.get(
    "/{event_id}",
    response_model=EventInResponse,
    name="events:get-event",
)
async def get_event(event_id: int):
    pass


@router.post(
    "",
    response_model=EventInResponse,
    name="events:create-event",
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
        event_create: EventInCreate = Body(..., embed=True, alias="event"),
        user: UserInDB = Depends(get_current_user_authorizer(required=True)),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> EventInResponse:
    event = await events_repo.create_event(**event_create.__dict__, author=user)

    return EventInResponse(
        event=event
    )


@router.put(
    "/{event_id}",
    response_model=EventInResponse,
    name="events:update-event",
)
async def update_event(event_id: int):
    pass


@router.delete(
    "/{event_id}",
    response_model=EventInResponse,
    name="events:delete-event",
)
async def delete_event(event_id: int):
    pass
