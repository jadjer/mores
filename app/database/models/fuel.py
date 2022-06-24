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

from sqlalchemy import Boolean, Column, Integer, Enum, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.domain.fuel import FuelType


class FuelModel(Base):
    __tablename__ = "fuel"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    mileage = Column(Integer, nullable=False)
    fuel_type = Column(Enum(FuelType), default=FuelType.PETROL_95)

    is_full = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vehicle = relationship("VehicleModel")
    location = relationship("LocationModel")
