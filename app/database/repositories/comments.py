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

from loguru import logger
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityDeleteError,
    EntityUpdateError,
)
from app.database.models import CommentModel
from app.database.repositories.base import BaseRepository
from app.models.domain.comment import Comment
from app.models.domain.user import User


class CommentsRepository(BaseRepository):

    async def create_comment_by_post_id_and_user(self, post_id: int, user: User, *, body: str) -> Comment:
        new_comment = CommentModel()
        new_comment.post_id = post_id
        new_comment.author_id = user.id
        new_comment.body = body

        self.session.add(new_comment)

        try:
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityCreateError from exception

        return await self.get_comment_by_id_and_post_id(new_comment.id, post_id)

    async def create_comment_by_event_id_and_user(self, event_id: int, user: User, *, body: str) -> Comment:
        new_comment = CommentModel()
        new_comment.event_id = event_id
        new_comment.author_id = user.id
        new_comment.body = body

        self.session.add(new_comment)

        try:
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityCreateError from exception

        return await self.get_comment_by_id_and_event_id(new_comment.id, event_id)

    async def get_comment_by_id(self, comment_id: int) -> Comment:
        query = select(CommentModel).where(
            CommentModel.id == comment_id,
        ).options(
            joinedload(CommentModel.author)
        )
        result = await self.session.execute(query)

        comment_in_db = result.scalars().first()
        if not comment_in_db:
            raise EntityDoesNotExists

        return self._convert_comment_model_to_comment(comment_in_db)

    async def get_comment_by_id_and_post_id(self, comment_id: int, post_id: int) -> Comment:
        query = select(CommentModel).where(
            and_(
                CommentModel.id == comment_id,
                CommentModel.post_id == post_id
            )
        ).options(
            joinedload(CommentModel.author)
        )
        result = await self.session.execute(query)

        comment_in_db = result.scalars().first()
        if not comment_in_db:
            raise EntityDoesNotExists

        return self._convert_comment_model_to_comment(comment_in_db)

    async def get_comment_by_id_and_event_id(self, comment_id: int, event_id: int) -> Comment:
        query = select(CommentModel).where(
            and_(
                CommentModel.id == comment_id,
                CommentModel.event_id == event_id
            )
        ).options(
            joinedload(CommentModel.author)
        )
        result = await self.session.execute(query)

        comment_in_db = result.scalars().first()
        if not comment_in_db:
            raise EntityDoesNotExists

        return self._convert_comment_model_to_comment(comment_in_db)

    async def get_comments_by_post_id(self, post_id: int) -> List[Comment]:
        query = select(CommentModel).where(
            CommentModel.post_id == post_id
        ).options(
            joinedload(CommentModel.author)
        )
        result = await self.session.execute(query)

        comments_in_db = result.scalars().all()
        comment_in_db: CommentModel

        return [self._convert_comment_model_to_comment(comment_in_db) for comment_in_db in comments_in_db]

    async def get_comments_by_event_id(self, event_id: int) -> List[Comment]:
        query = select(CommentModel).where(
            CommentModel.event_id == event_id
        ).options(
            joinedload(CommentModel.author)
        )
        result = await self.session.execute(query)

        comments_in_db = result.scalars().all()
        comment_in_db: CommentModel

        return [self._convert_comment_model_to_comment(comment_in_db) for comment_in_db in comments_in_db]

    async def update_comment_by_id_and_user(self, comment_id: int, user: User, *, body: str) -> Comment:
        comment_in_db: CommentModel = await self._get_comment_model_by_id_and_user(comment_id, user)
        comment_in_db.body = body

        try:
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityUpdateError from exception

        return self._convert_comment_model_to_comment(comment_in_db)

    async def delete_comment_by_id_and_user(self, comment_id: int, user: User) -> None:
        comment_in_db = await self._get_comment_model_by_id_and_user(comment_id, user)

        try:
            await self.session.delete(comment_in_db)
            await self.session.commit()
        except Exception as exception:
            logger.error(exception)
            raise EntityDeleteError from exception

    async def _get_comment_model_by_id_and_user(self, comment_id: int, user: User) -> CommentModel:
        query = select(CommentModel).where(
            and_(
                CommentModel.id == comment_id,
                CommentModel.author_id == user.id
            )
        ).options(
            joinedload(CommentModel.author)
        )

        result = await self.session.execute(query)

        comment_in_db: CommentModel = result.scalars().first()
        if not comment_in_db:
            raise EntityDoesNotExists

        return comment_in_db

    @staticmethod
    def _convert_comment_model_to_comment(comment_model: CommentModel) -> Comment:
        author = User(**comment_model.author.__dict__)
        comment = Comment(
            id=comment_model.id,
            author=author,
            body=comment_model.body,
            created_at=comment_model.created_at,
            updated_at=comment_model.updated_at,
        )
        return comment
