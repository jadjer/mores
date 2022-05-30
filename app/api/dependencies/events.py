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

from fastapi import Query, Path

from app.models.domain.event import EventState
from app.models.domain.event_confirmation import EventConfirmationType
from app.models.schemas.events import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    EventsFilter,
)


def get_events_filters(
        author: Optional[str] = None,
        state: EventState = EventState.PLANNED,
        limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
        offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> EventsFilter:
    return EventsFilter(
        author=author,
        state=state,
        limit=limit,
        offset=offset,
    )


def get_event_id_from_path(event_id: int = Path(..., ge=1)) -> int:
    return event_id


def get_event_confirmation_from_query(confirmation: EventConfirmationType = Query(...)) -> EventConfirmationType:
    return confirmation
