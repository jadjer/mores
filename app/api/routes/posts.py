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

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from app.api.dependencies.posts import (
    check_article_modification_permissions,
    get_post_by_id_from_path,
    get_posts_filters,
)
from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.repositories.posts import PostsRepository
from app.models.domain.post import Post
from app.models.domain.user import User
from app.models.schemas.post import (
    PostForResponse,
    PostInCreate,
    PostInResponse,
    PostInUpdate,
    PostsFilters,
    ListOfPostsInResponse,
)
from app.resources import strings
from app.services.posts import check_post_exists

router = APIRouter()


@router.get(
    "",
    response_model=ListOfPostsInResponse,
    name="posts:list-posts"
)
async def list_articles(
    articles_filters: PostsFilters = Depends(get_posts_filters),
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> ListOfPostsInResponse:
    pass
    # articles = await posts_repo.filter_articles(
    #     author=articles_filters.author,
    #     limit=articles_filters.limit,
    #     offset=articles_filters.offset,
    #     requested_user=user,
    # )
    # articles_for_response = [
    #     PostForResponse.from_orm(article) for article in articles
    # ]
    # return ListOfPostsInResponse(
    #     articles=articles_for_response,
    #     articles_count=len(articles),
    # )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PostInResponse,
    name="posts:create-article",
)
async def create_new_article(
    article_create: PostInCreate = Body(..., embed=True, alias="article"),
    user: User = Depends(get_current_user_authorizer()),
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> PostInResponse:
    pass
    # if await check_post_exists(posts_repo, slug):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=strings.ARTICLE_ALREADY_EXISTS,
    #     )
    #
    # article = await posts_repo.create_article(
    #     slug=slug,
    #     title=article_create.title,
    #     description=article_create.description,
    #     body=article_create.body,
    #     author=user,
    # )
    # return PostInResponse(article=PostForResponse.from_orm(article))


@router.get(
    "/{post_id}",
    response_model=PostInResponse,
    name="posts:get-article"
)
async def retrieve_article_by_slug(
    post: Post = Depends(get_post_by_id_from_path),
) -> PostInResponse:
    pass
    # return PostInResponse(article=PostForResponse.from_orm(post))


@router.put(
    "/{post_id}",
    response_model=PostInResponse,
    name="posts:update-article",
    dependencies=[Depends(check_article_modification_permissions)],
)
async def update_article_by_slug(
    article_update: PostInUpdate = Body(..., embed=True, alias="article"),
    current_post: Post = Depends(get_post_by_id_from_path),
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> PostInResponse:
    pass
    # slug = get_slug_for_article(article_update.title) if article_update.title else None
    # post = await posts_repo.update_article(
    #     article=current_post,
    #     slug=slug,
    #     **article_update.dict(),
    # )
    # return PostInResponse(post=PostForResponse.from_orm(post))


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="posts:delete-article",
    dependencies=[Depends(check_article_modification_permissions)],
    response_class=Response,
)
async def delete_article_by_slug(
    post: Post = Depends(get_post_by_id_from_path),
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> None:
    pass
    # await posts_repo.delete_article(article=post)
