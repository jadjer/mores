from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.domain.post import Post
from app.models.schemas.rwschema import RWSchema

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class PostForResponse(RWSchema, Post):
    pass


class PostInResponse(RWSchema):
    post: PostForResponse


class PostInCreate(RWSchema):
    title: str
    description: str
    body: str


class PostInUpdate(RWSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None


class ListOfPostsInResponse(RWSchema):
    posts: List[PostForResponse]
    posts_count: int


class PostsFilters(BaseModel):
    tag: Optional[str] = None
    author: Optional[str] = None
    limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)
