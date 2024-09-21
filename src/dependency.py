from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session as SQLModelSession

from src.extension import engine
from src.model import TokenPayload, User
from src.setting import settings

if TYPE_CHECKING:
    from collections.abc import Generator


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.BASE_URL}/login/access-token"
)


def get_db() -> Generator[SQLModelSession, None, None]:
    with SQLModelSession(engine) as session:
        yield session


Session = Annotated[SQLModelSession, Depends(get_db)]
Token = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: Session, token: Token) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ENCODING_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from exc

    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )

    return current_user
