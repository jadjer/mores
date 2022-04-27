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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import ProfileModel
from ..schemas import Profile
from ..cruds import *

from ..dependencies import get_db

router = APIRouter(prefix="/profile")


@router.get("/", tags=["profile"], response_model=Profile)
async def get_profile(db: Session = Depends(get_db)):
    db_profile = get_user(db)
    if not db_profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    return db_profile


@router.post("/create", tags=["profile"])
async def create_profile(profile: Profile, db: Session = Depends(get_db)):
    db_profile = create_user(db, profile)

    return profile


