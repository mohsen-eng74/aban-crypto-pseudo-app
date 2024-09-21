from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Annotated, Any, Self

from pydantic import constr, field_validator
from sqlmodel import DECIMAL, CheckConstraint, Column, Computed, Field, SQLModel


class Transaction(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    currency: Annotated[str, constr(to_upper=True)]
    price: Decimal = Field(ge=0, sa_column=Column("price", DECIMAL, nullable=False))
    volume: Decimal = Field(ge=0, sa_column=Column("volume", DECIMAL, nullable=False))
    value: Decimal = Field(
        ge=0,
        sa_column=Column("value", DECIMAL, Computed("price * volume"), nullable=False),
    )
    is_settled: bool = False

    # NOTE: https://plainenglish.io/community/creating-table-constraints-with-sqlmodel
    __table_args__ = (
        CheckConstraint(price.sa_column >= 0),  # type: ignore[attr-defined]
        CheckConstraint(volume.sa_column >= 0),  # type: ignore[attr-defined]
        CheckConstraint(value.sa_column >= 0),  # type: ignore[attr-defined]
    )

    @field_validator("currency", mode="before")
    @classmethod
    def make_uppercase(cls: type[Self], value: str | Any) -> str | Any:
        return value.upper() if isinstance(value, str) else value
