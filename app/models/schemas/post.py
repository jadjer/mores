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

from pydantic import BaseModel, Field

from app.models.domain.post import Post
from app.models.schemas.rwschema import RWSchema

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class PostInResponse(RWSchema):
    post: Post


class PostInCreate(RWSchema):
    title: str
    description: str
    thumbnail: str
    body: str


class PostInUpdate(RWSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    body: Optional[str] = None


class ListOfPostsInResponse(RWSchema):
    posts: List[Post]
    count: int


class PostsFilter(BaseModel):
    author: Optional[str] = None
    limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)
