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

from datetime import datetime
from typing import Optional, List
from pydantic import Field

from app.models.domain.event import Event, Location, EventState
from app.models.schemas.rwschema import RWSchema

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class EventInResponse(RWSchema):
    event: Event


class EventInCreate(RWSchema):
    title: str
    description: str
    thumbnail: str
    body: str
    started_at: datetime
    location: Location


class EventInUpdate(RWSchema):
    title: str
    description: str
    thumbnail: str
    body: str
    started_at: datetime
    location: Location
    state: EventState


class ListOfEventsInResponse(RWSchema):
    events: List[Event]
    events_count: int


class EventID(RWSchema):
    event_id: int = Field(1, ge=1)


class EventsFilter(RWSchema):
    state: EventState = EventState.PLANNED
    limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)
