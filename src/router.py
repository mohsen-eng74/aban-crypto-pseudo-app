from __future__ import annotations

from fastapi import APIRouter

from .route import currency_router, login_router, user_router

router = APIRouter()
router.include_router(login_router, prefix="/login", tags=["Auth"])

v1 = APIRouter(prefix="/v1")
v1.include_router(user_router, prefix="/users", tags=["Users"])
v1.include_router(currency_router, prefix="/currencies", tags=["Currencies"])


router.include_router(v1)
