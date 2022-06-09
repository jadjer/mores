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

from typing import List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityDeleteError,
    EntityUpdateError,
)
from app.database.models import CommentModel
from app.database.repositories.base import BaseRepository
from app.database.repositories.users import UsersRepository
from app.models.domain.comment import Comment


class CommentsRepository(BaseRepository):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._users_repo = UsersRepository(session)

    async def create_comment_by_post_id_and_user_id(self, post_id: int, user_id: int, body: str) -> Comment:
        new_comment = CommentModel()
        new_comment.post_id = post_id
        new_comment.author_id = user_id
        new_comment.body = body

        self.session.add(new_comment)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Comment(**new_comment.__dict__)

    async def get_comment_by_id(self, comment_id: int) -> Comment:
        comment_in_db = self.session.get(CommentModel, comment_id)
        if not comment_in_db:
            raise EntityDoesNotExists

        return Comment(**comment_in_db.__dict__)

    async def get_comments_by_post_id(self, post_id: int) -> List[Comment]:
        query = select(CommentModel).where(CommentModel.post_id == post_id)
        result = await self.session.execute(query)

        comments_in_db = result.scalars().all()

        return [Comment(**comment_in_db.__dict__) for comment_in_db in comments_in_db]

    async def update_comment_by_id_and_user_id(self, comment_id: int, user_id: int, body: str) -> Comment:
        comment_in_db: CommentModel = await self._get_comment_model_by_id_and_user_id(comment_id, user_id)
        comment_in_db.body = body

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Comment(**comment_in_db.__dict__)

    async def delete_comment_by_id_and_user_id(self, comment_id: int, user_id: int) -> None:
        comment_in_db = await self._get_comment_model_by_id_and_user_id(comment_id, user_id)

        try:
            await self.session.delete(comment_in_db)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_comment_model_by_id_and_user_id(self, comment_id: int, user_id: int) -> CommentModel:
        query = select(CommentModel).where(
            and_(
                CommentModel.id == comment_id,
                CommentModel.author_id == user_id
            )
        ).options(
            joinedload(CommentModel.post)
        )

        result = await self.session.execute(query)

        comment_in_db: CommentModel = result.scalars().first()
        if not comment_in_db:
            raise EntityDoesNotExists

        return comment_in_db
