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

from app.database.errors import EntityDoesNotExists
from app.database.repositories.posts import PostsRepository
from app.models.domain.post import Post
from app.models.domain.user import User


async def check_post_exists(posts_repo: PostsRepository, post_id: int) -> bool:
    try:
        await posts_repo.get_post_by_id(post_id)
    except EntityDoesNotExists:
        return False

    return True


def check_user_can_modify_post(user: User, post: Post) -> bool:
    return post.author.id == user.id
