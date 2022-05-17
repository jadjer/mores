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

from typing import List, Optional, Sequence, Union

from sqlalchemy.orm import Session

from app.database.errors import EntityDoesNotExist
from app.database.models import *
from app.database.repositories.base import BaseRepository
from app.database.repositories.user import UserRepository
from app.models.domain.post import Post
from app.models.domain.user import User

AUTHOR_USERNAME_ALIAS = "author_username"
SLUG_ALIAS = "slug"

CAMEL_OR_SNAKE_CASE_TO_WORDS = r"^[a-z\d_\-]+|[A-Z\d_\-][^A-Z\d_\-]*"


class PostRepository(BaseRepository):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._users_repo = UsersRepository(session)

    async def create_post(self, author: User, title: str, description: str, thumbnail: str, body: str) -> Post:
        new_post = PostModel(
            author_id=author.id,
            title=title,
            description=description,
            thumbnail=thumbnail,
            body=body
        )

        self.session.add(new_post)
        self.session.commit()

        return await self._get_article_from_db_record(
            article_row=article_row,
            slug=slug,
            author_username=article_row[AUTHOR_USERNAME_ALIAS],
            requested_user=author,
        )

    async def update_article(  # noqa: WPS211
            self,
            *,
            article: Post,
            slug: Optional[str] = None,
            title: Optional[str] = None,
            body: Optional[str] = None,
            description: Optional[str] = None,
    ) -> Post:
        updated_article = article.copy(deep=True)
        updated_article.slug = slug or updated_article.slug
        updated_article.title = title or article.title
        updated_article.body = body or article.body
        updated_article.description = description or article.description

        async with self.connection.transaction():
            updated_article.updated_at = await queries.update_article(
                self.connection,
                slug=article.slug,
                author_username=article.author.username,
                new_slug=updated_article.slug,
                new_title=updated_article.title,
                new_body=updated_article.body,
                new_description=updated_article.description,
            )

        return updated_article

    async def delete_article(self, *, article: Post) -> None:
        async with self.connection.transaction():
            await queries.delete_article(
                self.connection,
                slug=article.slug,
                author_username=article.author.username,
            )

    async def filter_articles(  # noqa: WPS211
            self,
            *,
            tag: Optional[str] = None,
            author: Optional[str] = None,
            favorited: Optional[str] = None,
            limit: int = 20,
            offset: int = 0,
            requested_user: Optional[User] = None,
    ) -> List[Post]:
        query_params: List[Union[str, int]] = []
        query_params_count = 0

        # fmt: off
        query = Query.from_(
            articles,
        ).select(
            articles.id,
            articles.slug,
            articles.title,
            articles.description,
            articles.body,
            articles.created_at,
            articles.updated_at,
            Query.from_(
                users,
            ).where(
                users.id == articles.author_id,
            ).select(
                users.username,
            ).as_(
                AUTHOR_USERNAME_ALIAS,
            ),
        )
        # fmt: on

        if tag:
            query_params.append(tag)
            query_params_count += 1

            # fmt: off
            query = query.join(
                articles_to_tags,
            ).on(
                (articles.id == articles_to_tags.article_id) & (
                        articles_to_tags.tag == Query.from_(
                    tags_table,
                ).where(
                    tags_table.tag == Parameter(query_params_count),
                ).select(
                    tags_table.tag,
                )
                ),
            )
            # fmt: on

        if author:
            query_params.append(author)
            query_params_count += 1

            # fmt: off
            query = query.join(
                users,
            ).on(
                (articles.author_id == users.id) & (
                        users.id == Query.from_(
                    users,
                ).where(
                    users.username == Parameter(query_params_count),
                ).select(
                    users.id,
                )
                ),
            )
            # fmt: on

        if favorited:
            query_params.append(favorited)
            query_params_count += 1

            # fmt: off
            query = query.join(
                favorites,
            ).on(
                (articles.id == favorites.article_id) & (
                        favorites.user_id == Query.from_(
                    users,
                ).where(
                    users.username == Parameter(query_params_count),
                ).select(
                    users.id,
                )
                ),
            )
            # fmt: on

        query = query.limit(Parameter(query_params_count + 1)).offset(
            Parameter(query_params_count + 2),
        )
        query_params.extend([limit, offset])

        articles_rows = await self.connection.fetch(query.get_sql(), *query_params)

        return [
            await self._get_article_from_db_record(
                article_row=article_row,
                slug=article_row[SLUG_ALIAS],
                author_username=article_row[AUTHOR_USERNAME_ALIAS],
                requested_user=requested_user,
            )
            for article_row in articles_rows
        ]

    async def get_articles_for_user_feed(
            self,
            *,
            user: User,
            limit: int = 20,
            offset: int = 0,
    ) -> List[Post]:
        articles_rows = await queries.get_articles_for_feed(
            self.connection,
            follower_username=user.username,
            limit=limit,
            offset=offset,
        )
        return [
            await self._get_article_from_db_record(
                article_row=article_row,
                slug=article_row[SLUG_ALIAS],
                author_username=article_row[AUTHOR_USERNAME_ALIAS],
                requested_user=user,
            )
            for article_row in articles_rows
        ]

    async def get_article_by_slug(
            self,
            *,
            slug: str,
            requested_user: Optional[User] = None,
    ) -> Post:
        article_row = await queries.get_article_by_slug(self.connection, slug=slug)
        if article_row:
            return await self._get_article_from_db_record(
                article_row=article_row,
                slug=article_row[SLUG_ALIAS],
                author_username=article_row[AUTHOR_USERNAME_ALIAS],
                requested_user=requested_user,
            )

        raise EntityDoesNotExist("article with slug {0} does not exist".format(slug))

    async def get_tags_for_article_by_slug(self, *, slug: str) -> List[str]:
        tag_rows = await queries.get_tags_for_article_by_slug(
            self.connection,
            slug=slug,
        )
        return [row["tag"] for row in tag_rows]

    async def get_favorites_count_for_article_by_slug(self, *, slug: str) -> int:
        return (
            await queries.get_favorites_count_for_article(self.connection, slug=slug)
        )["favorites_count"]

    async def is_article_favorited_by_user(self, *, slug: str, user: User) -> bool:
        return (
            await queries.is_article_in_favorites(
                self.connection,
                username=user.username,
                slug=slug,
            )
        )["favorited"]

    async def add_article_into_favorites(self, *, article: Post, user: User) -> None:
        await queries.add_article_to_favorites(
            self.connection,
            username=user.username,
            slug=article.slug,
        )

    async def remove_article_from_favorites(
            self,
            *,
            article: Post,
            user: User,
    ) -> None:
        await queries.remove_article_from_favorites(
            self.connection,
            username=user.username,
            slug=article.slug,
        )
