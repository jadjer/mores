from typing import Callable, Type

from fastapi import Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository


def _get_db_session(request: Request) -> Session:
    return request.app.state.database_session


def get_repository(repo_type: Type[BaseRepository]) -> Callable[[Session], BaseRepository]:
    def _get_repo(session: Session = Depends(_get_db_session)) -> BaseRepository:
        return repo_type(session)

    return _get_repo
