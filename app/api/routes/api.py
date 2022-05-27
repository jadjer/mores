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

from fastapi import APIRouter

from app.api.routes import (
    authentication,
    users,
    vehicles,
    services,
    service_types,
    reminders,
    fuels,
    geos,
    posts,
    comments,
    events,
    event_confirmations
)

router = APIRouter()
router.include_router(authentication.router, tags=["authentication"], prefix="/auth")
router.include_router(users.router, tags=["users"], prefix="/user")
router.include_router(vehicles.router, tags=["vehicles"], prefix="/vehicles")
router.include_router(services.router, tags=["services"], prefix="/services")
router.include_router(service_types.router, tags=["service_types"], prefix="/services/types")
router.include_router(reminders.router, tags=["reminders"], prefix="/services/reminders")
router.include_router(fuels.router, tags=["fuels"], prefix="/services/fuels")
router.include_router(geos.router, tags=["geos"], prefix="/geos")
router.include_router(posts.router, tags=["posts"], prefix="/posts")
router.include_router(comments.router, tags=["comments"], prefix="/posts/{post_id}/comments")
router.include_router(events.router, tags=["events"], prefix="/events")
router.include_router(event_confirmations.router, tags=["events"], prefix="/events/{event_id}/confirm")
