from __future__ import annotations

from sqlmodel import Session, select

from src.model import User, UserCreate
from src.util.jwt import get_password_hash, verify_password


def create_new_user(*, session: Session, user_detail: UserCreate) -> User:
    new_user = User.model_validate(
        user_detail,
        update={"hashed_password": get_password_hash(password=user_detail.password)},
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def authenticate_user(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)

    if not db_user:
        return None

    if not verify_password(
        plain_password=password, hashed_password=db_user.hashed_password
    ):
        return None

    return db_user
