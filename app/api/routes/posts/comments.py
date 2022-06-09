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

from fastapi import APIRouter, Body, Depends, Response, status, HTTPException

from app.api.dependencies.comments import check_comment_modification_permissions
from app.api.dependencies.get_id_from_path import (
    get_comment_id_from_path,
    get_post_id_from_path,
)
from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.errors import EntityCreateError
from app.database.repositories.comments import CommentsRepository
from app.models.schemas.comment import (
    CommentInCreate,
    CommentInResponse,
    ListOfCommentsInResponse,
    CommentInUpdate,
)
from app.resources import strings

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentInResponse,
    name="comments:create-comment-for-post",
)
async def create_comment(
        post_id: int = Depends(get_post_id_from_path),
        comment_create: CommentInCreate = Body(..., embed=True, alias="comment"),
        user_id: int = Depends(get_current_user_authorizer()),
        comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> CommentInResponse:
    comment_create_error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.COMMENT_CREATE_ERROR)

    try:
        comment = await comments_repo.create_comment_by_post_id_and_user_id(post_id, user_id, **comment_create.__dict__)
    except EntityCreateError as exception:
        raise comment_create_error from exception

    return CommentInResponse(comment=comment)


@router.get(
    "",
    response_model=ListOfCommentsInResponse,
    name="comments:get-comments-for-post",
)
async def get_comments(
        post_id: int = Depends(get_post_id_from_path),
        comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> ListOfCommentsInResponse:
    comments = await comments_repo.get_comments_by_post_id(post_id)
    return ListOfCommentsInResponse(comments=comments)


@router.put(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="comments:update-comment-from-post",
    dependencies=[
        Depends(check_comment_modification_permissions)
    ],
    response_class=Response,
)
async def update_comment(
        comment_id: int = Depends(get_comment_id_from_path),
        comment_update: CommentInUpdate = Body(..., embed=True, alias="comment"),
        user_id: int = Depends(get_current_user_authorizer()),
        comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> None:
    await comments_repo.update_comment_by_id_and_user_id(comment_id, user_id, **comment_update.__dict__)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="comments:delete-comment-from-post",
    dependencies=[
        Depends(check_comment_modification_permissions)
    ],
    response_class=Response,
)
async def delete_comment(
        comment_id: int = Depends(get_comment_id_from_path),
        user_id: int = Depends(get_current_user_authorizer()),
        comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> None:
    await comments_repo.delete_comment_by_id_and_user_id(comment_id, user_id)
