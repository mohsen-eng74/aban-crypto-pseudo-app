from __future__ import annotations

from dynaconf import Validator

validators = [
    Validator(
        "ENVIRONMENT",
        must_exist=True,
        is_in={"production", "staging", "development"},
    ),
    Validator(
        "SECRET_KEY",
        "SUPERUSER_EMAIL",
        "SUPERUSER_PASSWORD",
        "SQLALCHEMY_DATABASE_URI",
        must_exist=True,
        ne=None,
    ),
]
