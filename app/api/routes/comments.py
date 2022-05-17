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

from fastapi import APIRouter, Body, Depends, Response
from starlette import status

from app.api.dependencies.articles import get_article_by_slug_from_path
from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.comments import (
    check_comment_modification_permissions,
    get_comment_by_id_from_path,
)
from app.api.dependencies.database import get_repository
from app.database.repositories.comment import CommentsRepository
from app.models.domain.post import Post
from app.models.domain.comment import Comment
from app.models.domain.user import User
from app.models.schemas.comment import (
    CommentInCreate,
    CommentInResponse,
    ListOfCommentsInResponse,
)

router = APIRouter()


@router.get(
    "",
    response_model=ListOfCommentsInResponse,
    name="comments:get-comments-for-article",
)
async def list_comments_for_article(
    article: Post = Depends(get_article_by_slug_from_path),
    user: Optional[User] = Depends(get_current_user_authorizer(required=False)),
    comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> ListOfCommentsInResponse:
    comments = await comments_repo.get_comments_for_article(article=article, user=user)
    return ListOfCommentsInResponse(comments=comments)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentInResponse,
    name="comments:create-comment-for-article",
)
async def create_comment_for_article(
    comment_create: CommentInCreate = Body(..., embed=True, alias="comment"),
    article: Post = Depends(get_article_by_slug_from_path),
    user: User = Depends(get_current_user_authorizer()),
    comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> CommentInResponse:
    comment = await comments_repo.create_comment_for_article(
        body=comment_create.body,
        article=article,
        user=user,
    )
    return CommentInResponse(comment=comment)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="comments:delete-comment-from-article",
    dependencies=[Depends(check_comment_modification_permissions)],
    response_class=Response,
)
async def delete_comment_from_article(
    comment: Comment = Depends(get_comment_by_id_from_path),
    comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> None:
    await comments_repo.delete_comment(comment=comment)
