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

import enum
from sqlalchemy import Column, Integer, ForeignKey, Enum

from app.database.base import Base


class EventConfirmationType(enum.Enum):
    YES = 1
    MAY_BE_YES = 2
    MAY_BE = 3
    MAY_BE_NO = 4
    NO = 5


class EventConfirmationModel(Base):
    __tablename__ = "event_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmation_type = Column(Enum(EventConfirmationType), default=EventConfirmationType.MAY_BE)
