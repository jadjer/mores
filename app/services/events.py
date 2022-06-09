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

from app.database.errors import EntityDoesNotExists
from app.database.repositories.events import EventsRepository
from app.database.repositories.events_confirmations import EventConfirmationsRepository
from app.models.domain.event import Event


async def check_event_exist_by_id(events_repo: EventsRepository, event_id: int) -> bool:
    try:
        await events_repo.get_event_by_id(event_id)
    except EntityDoesNotExists:
        return False

    return True


def check_user_can_modify_event(user_id: int, event: Event) -> bool:
    return event.author.user_id == user_id


async def check_event_confirmation_exists(
        events_confirmation_repo: EventConfirmationsRepository,
        event_id: int,
        user_id: int
) -> bool:
    try:
        await events_confirmation_repo.get_confirmation_by_event_id_and_user_id(event_id, user_id)
    except EntityDoesNotExists:
        return False

    return True
