from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any, Self

from pydantic import constr, field_validator
from sqlmodel import Field, SQLModel


class CurrencyPurchaseRequest(SQLModel):
    name: Annotated[str, constr(to_upper=True)]
    volume: Decimal = Field(ge=0)

    @field_validator("name", mode="before")
    @classmethod
    def make_uppercase(cls: type[Self], value: str | Any) -> str | Any:
        return value.upper() if isinstance(value, str) else value
