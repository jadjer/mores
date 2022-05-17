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

from enum import Enum

import datetime as datetime

from app.models.common import IDModelMixin, DateTimeModelMixin
from app.models.domain.geo import Geo
from app.models.domain.rwmodel import RWModel
from app.models.domain.user import User


class EventState(Enum):
    PLANNED = 1
    DONE = 2
    CANCELED = 3


class Event(IDModelMixin, DateTimeModelMixin, RWModel):
    author: User
    title: str
    description: str
    picture: str
    body: str
    start_at: datetime.datetime
    geo: Geo
    state: EventState