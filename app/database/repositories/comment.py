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

from typing import List, Optional

from app.database.errors import EntityDoesNotExist
from app.database.repositories.base import BaseRepository
from app.database.repositories.user import UsersRepository
from app.models.domain.post import Post
from app.models.domain.comment import Comment
from app.models.domain.user import User


class CommentRepository(BaseRepository):

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)
        self._profiles_repo = UsersRepository(conn)

    async def get_comment_by_id(
        self,
        *,
        comment_id: int,
        article: Post,
        user: Optional[User] = None,
    ) -> Comment:
        comment_row = await queries.get_comment_by_id_and_slug(
            self.connection,
            comment_id=comment_id,
            article_slug=article.slug,
        )
        if comment_row:
            return await self._get_comment_from_db_record(
                comment_row=comment_row,
                author_username=comment_row["author_username"],
                requested_user=user,
            )

        raise EntityDoesNotExist(
            "comment with id {0} does not exist".format(comment_id),
        )

    async def get_comments_for_article(
        self,
        *,
        article: Post,
        user: Optional[User] = None,
    ) -> List[Comment]:
        comments_rows = await queries.get_comments_for_article_by_slug(
            self.connection,
            slug=article.slug,
        )
        return [
            await self._get_comment_from_db_record(
                comment_row=comment_row,
                author_username=comment_row["author_username"],
                requested_user=user,
            )
            for comment_row in comments_rows
        ]

    async def create_comment_for_article(
        self,
        *,
        body: str,
        article: Post,
        user: User,
    ) -> Comment:
        comment_row = await queries.create_new_comment(
            self.connection,
            body=body,
            article_slug=article.slug,
            author_username=user.username,
        )
        return await self._get_comment_from_db_record(
            comment_row=comment_row,
            author_username=comment_row["author_username"],
            requested_user=user,
        )

    async def delete_comment(self, *, comment: Comment) -> None:
        await queries.delete_comment_by_id(
            self.connection,
            comment_id=comment.id_,
            author_username=comment.author.username,
        )

    async def _get_comment_from_db_record(
        self,
        *,
        comment_row: Record,
        author_username: str,
        requested_user: Optional[User],
    ) -> Comment:
        return Comment(
            id_=comment_row["id"],
            body=comment_row["body"],
            author=await self._profiles_repo.get_profile_by_username(
                username=author_username,
                requested_user=requested_user,
            ),
            created_at=comment_row["created_at"],
            updated_at=comment_row["updated_at"],
        )
