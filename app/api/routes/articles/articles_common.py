from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.articles import get_article_by_slug_from_path
from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.repositories.posts import ArticlesRepository
from app.models.domain.posts import Post
from app.models.domain.users import User
from app.models.schemas.posts import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    PostForResponse,
    PostInResponse,
    ListOfPostsInResponse,
)
from app.resources import strings

router = APIRouter()


@router.get(
    "/feed",
    response_model=ListOfPostsInResponse,
    name="articles:get-user-feed-articles",
)
async def get_articles_for_user_feed(
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
    user: User = Depends(get_current_user_authorizer()),
    articles_repo: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> ListOfPostsInResponse:
    articles = await articles_repo.get_articles_for_user_feed(
        user=user,
        limit=limit,
        offset=offset,
    )
    articles_for_response = [
        PostForResponse(**article.dict()) for article in articles
    ]
    return ListOfPostsInResponse(
        articles=articles_for_response,
        articles_count=len(articles),
    )


@router.post(
    "/{slug}/favorite",
    response_model=PostInResponse,
    name="articles:mark-article-favorite",
)
async def mark_article_as_favorite(
    article: Post = Depends(get_article_by_slug_from_path),
    user: User = Depends(get_current_user_authorizer()),
    articles_repo: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> PostInResponse:
    if not article.favorited:
        await articles_repo.add_article_into_favorites(article=article, user=user)

        return PostInResponse(
            article=PostForResponse.from_orm(
                article.copy(
                    update={
                        "favorited": True,
                        "favorites_count": article.favorites_count + 1,
                    },
                ),
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.ARTICLE_IS_ALREADY_FAVORITED,
    )


@router.delete(
    "/{slug}/favorite",
    response_model=PostInResponse,
    name="articles:unmark-article-favorite",
)
async def remove_article_from_favorites(
    article: Post = Depends(get_article_by_slug_from_path),
    user: User = Depends(get_current_user_authorizer()),
    articles_repo: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> PostInResponse:
    if article.favorited:
        await articles_repo.remove_article_from_favorites(article=article, user=user)

        return PostInResponse(
            article=PostForResponse.from_orm(
                article.copy(
                    update={
                        "favorited": False,
                        "favorites_count": article.favorites_count - 1,
                    },
                ),
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.ARTICLE_IS_NOT_FAVORITED,
    )
