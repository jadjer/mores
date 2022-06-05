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

from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.database.base import Base


class ReminderModel(Base):
    __tablename__ = "reminder"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id"), nullable=False)
    service_type_id = Column(Integer, ForeignKey("service_type.id"), nullable=False)
    next_mileage = Column(Integer, nullable=False)
    next_date = Column(Date, nullable=False)

    vehicle = relationship("VehicleModel")
    service_type = relationship("ServiceTypeModel")
