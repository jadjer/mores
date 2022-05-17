from slugify import slugify

from app.database.errors import EntityDoesNotExist
from app.database.repositories.post import ArticlesRepository
from app.models.domain.post import Post
from app.models.domain.user import User


async def check_article_exists(articles_repo: ArticlesRepository, slug: str) -> bool:
    try:
        await articles_repo.get_article_by_slug(slug=slug)
    except EntityDoesNotExist:
        return False

    return True


def get_slug_for_article(title: str) -> str:
    return slugify(title)


def check_user_can_modify_article(article: Post, user: User) -> bool:
    return article.author.username == user.username
