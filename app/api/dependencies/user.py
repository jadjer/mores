from typing import Optional

from fastapi import Depends, HTTPException, Path, status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.errors import EntityDoesNotExist
from app.database.repositories.users import UsersRepository
from app.models.domain.user import User
from app.resources import strings


async def get_user_by_username_from_path(
    username: str = Path(..., min_length=1),
    user: Optional[User] = Depends(get_current_user_authorizer(required=False)),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> User:
    try:
        return await users_repo.get_user_by_username(
            username=username,
            requested_user=user,
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.USER_DOES_NOT_EXIST_ERROR,
        )
