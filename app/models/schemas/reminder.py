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

from datetime import date
from typing import List, Optional

from app.models.domain.reminder import Reminder
from app.models.schemas.rwschema import RWSchema


class ListOfRemindersInResponse(RWSchema):
    reminders: List[Reminder]
    count: int


class ReminderInResponse(RWSchema):
    reminder: Reminder


class ReminderInCreate(RWSchema):
    service_type_id: int
    next_mileage: int
    next_date: date


class ReminderInUpdate(RWSchema):
    service_type_id: Optional[int] = None
    next_mileage: Optional[int] = None
    next_date: Optional[date] = None
