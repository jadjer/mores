from fastapi import APIRouter

from app.api.routes import main
# from app.api.routes import authentication, comments, tags, users
# from app.api.routes.articles import api as articles

router = APIRouter()
router.include_router(main.router, tags=["main"], prefix="/test")
# router.include_router(authentication.router, tags=["authentication"], prefix="/users")
# router.include_router(users.router, tags=["users"], prefix="/user")
# router.include_router(articles.router, tags=["articles"])
# router.include_router(
#     comments.router,
#     tags=["comments"],
#     prefix="/articles/{slug}/comments",
# )
# router.include_router(tags.router, tags=["tags"], prefix="/tags")
