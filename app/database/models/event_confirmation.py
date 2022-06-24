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

from sqlalchemy import Column, Integer, ForeignKey, Enum, func, DateTime
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.domain.event_confirmation import EventConfirmationType


class EventConfirmationModel(Base):
    __tablename__ = "event_confirmation"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    confirmation_type = Column(Enum(EventConfirmationType), default=EventConfirmationType.MAY_BY)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    event = relationship("EventModel")
    user = relationship("UserModel")
