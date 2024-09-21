from __future__ import annotations

import datetime
from typing import Any

import jwt
from passlib.context import CryptContext

from src.setting import settings

PASSWORD_HASHING_CONTEXT = CryptContext(
    schemes=["bcrypt"], default="bcrypt", deprecated="auto"
)


def create_access_token(
    *, subject: str | Any, expires_delta: datetime.timedelta
) -> str:
    expire = datetime.datetime.now(datetime.UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}

    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ENCODING_ALGORITHM
    )


def verify_password(*, plain_password: str, hashed_password: str) -> bool:
    return PASSWORD_HASHING_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(*, password: str) -> str:
    return PASSWORD_HASHING_CONTEXT.hash(password)
