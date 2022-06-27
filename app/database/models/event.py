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

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    func,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.domain.event import EventState


class EventModel(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)

    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    body = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    event_state = Column(Enum(EventState), default=EventState.PLANNED)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("UserModel")
    location = relationship("LocationModel")
