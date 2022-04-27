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

from sqlalchemy.orm import Session

from ..models import ProfileModel
from ..schemas import Profile, ProfileCreate


def get_user(db: Session, user_id: int):
    return db.query(ProfileModel).filter(ProfileModel.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(ProfileModel).filter(ProfileModel.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProfileModel).offset(skip).limit(limit).all()


def create_user(db: Session, profile: ProfileCreate):
    fake_hashed_password = profile.password + "notreallyhashed"
    db_user = ProfileModel(email=profile.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
