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

from fastapi import APIRouter, Body, Depends, HTTPException, status, Query, Path

from app.api.dependencies.authentication import get_current_profile_authorizer
from app.api.dependencies.database import get_repository
from app.database.errors import EntityDoesNotExists
from app.database.repositories.profiles import ProfilesRepository
from app.models.domain.profile import Profile
from app.models.schemas.profile import ProfileInUpdate, ProfileInResponse, ListOfProfileInResponse
from app.resources import strings
from app.services.profiles import check_username_is_taken

router = APIRouter()


@router.get(
    "",
    response_model=ListOfProfileInResponse,
    name="profiles:get-all-profiles",
    dependencies=[
        Depends(get_current_profile_authorizer())
    ]
)
async def get_profiles(
        limit: int = Query(20, ge=1),
        offset: int = Query(0, ge=0),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
) -> ListOfProfileInResponse:
    profiles = await profiles_repo.get_profiles_with_filter(limit, offset)
    return ListOfProfileInResponse(profiles=profiles, count=len(profiles))


@router.get(
    "/me",
    response_model=ProfileInResponse,
    name="profiles:get-my-profile"
)
async def get_my_profile(
        profile: Profile = Depends(get_current_profile_authorizer()),
) -> ProfileInResponse:
    return ProfileInResponse(profile=profile)


@router.get(
    "/{profile_id}",
    response_model=ProfileInResponse,
    name="profiles:get-profile",
    dependencies=[
        Depends(get_current_profile_authorizer())
    ]
)
async def get_profile_by_id(
        profile_id: int = Path(..., ge=1),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
) -> ProfileInResponse:
    request_error = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.PROFILE_DOES_NOT_EXISTS)

    try:
        profile = await profiles_repo.get_profile_by_id(profile_id)
    except EntityDoesNotExists as existence_error:
        raise request_error from existence_error

    return ProfileInResponse(profile=profile)


@router.put(
    "/me",
    response_model=ProfileInResponse,
    name="profiles:update-my-profile"
)
async def update_my_profile(
        profile_update: ProfileInUpdate = Body(..., embed=True, alias="user"),
        profile: Profile = Depends(get_current_profile_authorizer()),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
) -> ProfileInResponse:
    if profile_update.username:
        if await check_username_is_taken(profiles_repo, profile_update.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=strings.USERNAME_TAKEN,
            )

    profile = await profiles_repo.update_profile(profile.id, **profile_update.__dict__)

    return ProfileInResponse(profile=profile)
