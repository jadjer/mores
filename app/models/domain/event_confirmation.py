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

from app.models.domain.event import Event
from app.models.domain.rwmodel import RWModel
from app.models.domain.user import User


class EventConfirmationType(Enum):
    YES = 1
    MAY_BE_YES = 2
    MAY_BY = 3
    MAY_BE_NO = 4
    NO = 5


class EventConfirm(RWModel):
    event: Event
    user: User
    type: EventConfirmationType
