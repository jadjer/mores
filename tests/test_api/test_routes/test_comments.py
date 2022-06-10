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
from sqlalchemy.orm import Session

from app.database.repositories.comments import CommentsRepository
from app.database.repositories.profiles import ProfilesRepository
from app.models.domain.post import Post
from app.models.schemas.comment import CommentInResponse, ListOfCommentsInResponse

pytestmark = pytest.mark.asyncio


async def test_user_can_add_comment_for_post(app: FastAPI, authorized_client: AsyncClient, test_post: Post) -> None:
    created_comment_response = await authorized_client.post(
        app.url_path_for("comments:create-comment-for-post", post_id=str(test_post.id)),
        json={"comment": {"body": "comment"}},
    )

    created_comment = CommentInResponse(**created_comment_response.json())

    comments_for_post_response = await authorized_client.get(
        app.url_path_for("comments:get-comments-for-post", post_id=str(test_post.id))
    )

    comments = ListOfCommentsInResponse(**comments_for_post_response.json())

    assert created_comment.comment == comments.comments[0]


async def test_user_can_delete_own_comment(app: FastAPI, authorized_client: AsyncClient, test_post: Post) -> None:
    created_comment_response = await authorized_client.post(
        app.url_path_for("comments:create-comment-for-post", post_id=str(test_post.id)),
        json={"comment": {"body": "comment"}},
    )

    created_comment = CommentInResponse(**created_comment_response.json())

    await authorized_client.delete(
        app.url_path_for(
            "comments:delete-comment-from-post",
            post_id=str(test_post.id),
            comment_id=str(created_comment.comment.id))
    )

    comments_for_post_response = await authorized_client.get(
        app.url_path_for(
            "comments:get-comments-for-post",
            post_id=str(test_post.id)
        )
    )

    comments = ListOfCommentsInResponse(**comments_for_post_response.json())

    assert len(comments.comments) == 0


async def test_user_can_not_delete_not_authored_comment(
        app: FastAPI, authorized_client: AsyncClient, test_post: Post, session: Session
) -> None:
    profiles_repo = ProfilesRepository(session)
    profile = await profiles_repo.create_profile_and_user(
        username="test_author",
        email="author@email.com",
        password="password",
    )
    comments_repo = CommentsRepository(session)
    comment = await comments_repo.create_comment_by_post_id_and_user_id(test_post.id, profile.user_id, "tmp")

    forbidden_response = await authorized_client.delete(
        app.url_path_for(
            "comments:delete-comment-from-post",
            post_id=str(test_post.id),
            comment_id=str(comment.id),
        )
    )

    assert forbidden_response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_will_receive_error_for_not_existing_comment(
        app: FastAPI, authorized_client: AsyncClient, test_post: Post
) -> None:
    not_found_response = await authorized_client.delete(
        app.url_path_for(
            "comments:delete-comment-from-post",
            post_id=str(test_post.id),
            comment_id="1",
        )
    )

    assert not_found_response.status_code == status.HTTP_404_NOT_FOUND
