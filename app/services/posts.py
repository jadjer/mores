from app.database.errors import EntityDoesNotExist
from app.database.repositories.posts import PostsRepository
from app.models.domain.post import Post
from app.models.domain.user import User


async def check_post_exists(posts_repo: PostsRepository, post_id: int) -> bool:
    try:
        await posts_repo.get_article_by_id(slug=post_id)
    except EntityDoesNotExist:
        return False

    return True


def check_user_can_modify_post(article: Post, user: User) -> bool:
    return article.author.username == user.username
