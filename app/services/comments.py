from app.models.domain.comment import Comment
from app.models.domain.user import User


def check_user_can_modify_comment(comment: Comment, user: User) -> bool:
    return comment.author.username == user.username
