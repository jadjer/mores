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

from typing import Optional

from fastapi import Depends, HTTPException, Path, Query
from fastapi import status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.errors import EntityDoesNotExist
from app.database.repositories.posts import PostsRepository
from app.models.domain.post import Post
from app.models.domain.user import User
from app.models.schemas.post import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    PostsFilters,
)
from app.resources import strings
from app.services.posts import check_user_can_modify_post


def get_posts_filters(
    author: Optional[str] = None,
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> PostsFilters:
    return PostsFilters(
        author=author,
        limit=limit,
        offset=offset,
    )


async def get_post_by_id_from_path(
    post_id: str = Path(..., min_length=1),
    user: Optional[User] = Depends(get_current_user_authorizer(required=False)),
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> Post:
    try:
        return await posts_repo.get_article_by_slug(post_id=post_id, requested_user=user)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.ARTICLE_DOES_NOT_EXIST_ERROR,
        )


def check_article_modification_permissions(
    current_post: Post = Depends(get_post_by_id_from_path),
    user: User = Depends(get_current_user_authorizer()),
) -> None:
    if not check_user_can_modify_post(current_post, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.USER_IS_NOT_AUTHOR_OF_ARTICLE,
        )
