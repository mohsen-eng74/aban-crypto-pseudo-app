from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from src.dependency import CurrentUser, Session, get_current_active_superuser
from src.model import User, UserPublic, UsersPublic

user_router = APIRouter()


@user_router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@user_router.get("/me", response_model=UserPublic)
def get_logged_user(current_user: CurrentUser) -> Any:
    return current_user


@user_router.get("/{user_id}", response_model=UserPublic)
def get_user_by_id(user_id: str, session: Session, current_user: CurrentUser) -> Any:
    user = session.get(User, user_id)
    if user == current_user:
        return user

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user doesn't exist",
        )

    return user
