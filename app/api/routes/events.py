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

from fastapi import APIRouter, status, Depends, Body, HTTPException

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.events import (
    get_events_filters,
    get_event_id_from_path
)
from app.database.errors import EntityDoesNotExist
from app.database.repositories.events import EventsRepository
from app.models.domain.user import UserInDB
from app.models.schemas.events import (
    EventsFilter,
    ListOfEventsInResponse,
    EventInResponse,
    EventInCreate,
    EventInRequest,
    EventInUpdate,
)
from app.resources import strings

router = APIRouter()


@router.get(
    "",
    response_model=ListOfEventsInResponse,
    name="events:get-actual-events",
)
async def get_events(
        events_filter: EventsFilter = Depends(get_events_filters),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> ListOfEventsInResponse:
    try:
        events = await events_repo.filter_events(
            author=events_filter.author,
            state=events_filter.state,
            limit=events_filter.limit,
            offset=events_filter.offset
        )

    except EntityDoesNotExist:
        return ListOfEventsInResponse(events=[], events_count=0)

    return ListOfEventsInResponse(events=events, events_count=len(events))


@router.get(
    "/{event_id}",
    response_model=EventInResponse,
    name="events:get-event",
)
async def get_event(
        event_id: int = Depends(get_event_id_from_path),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> EventInResponse:
    wrong_event_id_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.EVENT_DOES_NOT_EXIST_ERROR
    )

    try:
        event = await events_repo.get_event(event_id)
    except EntityDoesNotExist as existence_error:
        raise wrong_event_id_error from existence_error

    return EventInResponse(event=event)


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

    return EventInResponse(event=event)


@router.put(
    "/{event_id}",
    response_model=EventInResponse,
    name="events:update-event",
)
async def update_event(
        event_id: int = Depends(get_event_id_from_path),
        event_create: EventInUpdate = Body(..., embed=True, alias="event"),
        user: UserInDB = Depends(get_current_user_authorizer(required=True)),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> EventInResponse:
    event = await events_repo.update_event(author=user, **event_create.__dict__)

    return EventInResponse(event=event)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="events:delete-event",
)
async def delete_event(
        event_id: int = Depends(get_event_id_from_path),
        user: UserInDB = Depends(get_current_user_authorizer(required=True)),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> None:
    await events_repo.delete_event(event_id)
