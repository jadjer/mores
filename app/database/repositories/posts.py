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

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

from app.database.errors import (
    EntityDoesNotExists,
    EntityDeleteError,
    EntityUpdateError,
    EntityCreateError,
)
from app.database.models import *
from app.database.repositories.base import BaseRepository
from app.database.repositories.profiles import ProfilesRepository
from app.models.domain.post import Post


class PostsRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session)
        self._profiles_repo = ProfilesRepository(session)

    async def create_post_by_user_id(
            self,
            user_id: int,
            title: str,
            body: str,
            description: Optional[str] = None,
            thumbnail: Optional[str] = None,
    ) -> Post:
        new_post = PostModel()
        new_post.author_id = user_id
        new_post.title = title
        new_post.description = description
        new_post.thumbnail = thumbnail
        new_post.body = body

        self.session.add(new_post)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Post(**new_post.__dict__)

    async def get_post_by_id(self, post_id: int) -> Post:
        post_in_db: PostModel = await self.session.get(PostModel, post_id)
        if not post_in_db:
            raise EntityDoesNotExists

        return Post(**post_in_db.__dict__)

    async def get_post_by_title(self, title: str) -> Post:
        query = select(PostModel).where(PostModel.title == title)
        result = await self.session.execute(query)

        post_in_db: PostModel = result.scalars().first()
        if not post_in_db:
            raise EntityDoesNotExists

        return Post(**post_in_db.__dict__)

    async def get_posts_with_filter(self, author: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Post]:
        query = select(PostModel)

        if author:
            profile_in_db = await self._profiles_repo.get_profile_by_username(author)
            query = query.where(PostModel.author_id == profile_in_db.user_id)

        query = query.limit(limit)
        query = query.offset(offset)
        query = query.options(
            joinedload(PostModel.author),
            joinedload(PostModel.comments)
        )

        result = await self.session.execute(query)
        posts_in_db: List[PostModel] = result.scalars().all()

        return [Post(**post_in_db.__dict__) for post_in_db in posts_in_db]

    async def update_post_by_id_and_user_id(
            self,
            post_id: int,
            user_id: int,
            title: Optional[str] = None,
            description: Optional[str] = None,
            thumbnail: Optional[str] = None,
            body: Optional[str] = None
    ) -> Post:
        post_in_db = await self._get_post_model_by_id(post_id, user_id)
        post_in_db.title = title or post_in_db.title
        post_in_db.description = description or post_in_db.description
        post_in_db.thumbnail = thumbnail or post_in_db.thumbnail
        post_in_db.body = body or post_in_db.body

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Post(**post_in_db.__dict__)

    async def delete_post(self, post_id: int, user_id: int) -> None:
        post_in_db = self._get_post_model_by_id(post_id, user_id)

        try:
            await self.session.delete(post_in_db)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_post_model_by_id(self, post_id: int, user_id: int) -> PostModel:
        query = select(PostModel).where(
            and_(
                PostModel.id == post_id,
                PostModel.author_id == user_id,
            )
        )

        result = await self.session.execute(query)

        post_model_in_db: PostModel = result.scalars().first()
        if not post_model_in_db:
            raise EntityDoesNotExists

        return post_model_in_db
