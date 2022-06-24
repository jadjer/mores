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

import pytest

from fastapi import FastAPI, status
from httpx import AsyncClient

from app.models.domain.vehicle import Vehicle


@pytest.mark.asyncio
async def test_user_can_add_vehicle(
        initialized_app: FastAPI, authorized_client: AsyncClient
) -> None:
    vehicle_data = {
        "brand": "honda",
        "model": "xl1000v",
        "gen": 3,
        "year": 2008,
        "color": "silver",
        "mileage": 65500,
        "vin": "JVM0935G46622",
        "registration_plate": "9112AB2",
        "name": "Bullfinch"
    }

    response = await authorized_client.post(
        initialized_app.url_path_for("vehicles:create-vehicle"), json={"vehicle": vehicle_data}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_unauthorised_user_can_not_add_vehicle(
        initialized_app: FastAPI, client: AsyncClient
) -> None:
    vehicle_data = {
        "brand": "honda",
        "model": "xl1000v",
        "gen": 3,
        "year": 2008,
        "color": "silver",
        "mileage": 65500,
        "vin": "JVM0935G46622",
        "registration_plate": "9112AB2",
        "name": "Bullfinch"
    }

    response = await client.post(
        initialized_app.url_path_for("vehicles:create-vehicle"), json={"vehicle": vehicle_data}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "parameter_name, parameter_value",
    (
            ("vin", "JVM01234567891011"),
            ("registration_plate", "9112AB2")
    ),
)
async def test_user_can_not_add_vehicle_with_duplicated_params(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_vehicle: Vehicle,
        parameter_name: str,
        parameter_value: str,
) -> None:
    vehicle_data = {
        "vehicle": {
            "brand": "honda",
            "model": "xl1000v",
            "gen": 3,
            "year": 2008,
            "color": "silver",
            "mileage": 65500,
            "vin": "JVM0935G46622",
            "registration_plate": "9112AB2",
            "name": "Bullfinch"
        }
    }

    vehicle_data["vehicle"][parameter_name] = parameter_value

    response = await authorized_client.post(
        initialized_app.url_path_for("vehicles:create-vehicle"), json=vehicle_data
    )

    assert response.status_code == status.HTTP_409_CONFLICT
