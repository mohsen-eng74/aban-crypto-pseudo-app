from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import EmailStr
from sqlmodel import DECIMAL, CheckConstraint, Column, Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserPublic(UserBase):
    id: str


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    hashed_password: str
    credit: Decimal = Field(
        default=1_000,  # TODO: default, MUST be revised
        ge=0,
        sa_column=Column("credit", DECIMAL, nullable=False),
    )

    # NOTE: https://plainenglish.io/community/creating-table-constraints-with-sqlmodel
    __table_args__ = (
        CheckConstraint(credit.sa_column >= 0),  # type: ignore[attr-defined]
    )
