from __future__ import annotations

import contextlib
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status

from src.constant import CURRENCIES_PRICE_MAPPING
from src.dependency import CurrentUser, Session
from src.model import CurrencyPurchaseRequest, Transaction, User
from src.util.settle import buy_from_exchange

logger = logging.getLogger(__name__)
currency_router = APIRouter()


@currency_router.post("/purchase/", status_code=status.HTTP_202_ACCEPTED)
async def purchase(
    request: CurrencyPurchaseRequest,
    session: Session,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
) -> Response:
    if request.name not in CURRENCIES_PRICE_MAPPING:
        raise HTTPException(status_code=404, detail="The Currency doesn't exist")

    try:
        # NOTE: refresh & lock the current user
        session.refresh(current_user, with_for_update=True)

        # NOTE: to prevent data inconsistency on concurrent update, do updates inplace in db
        # ref: https://python.plainenglish.io/optimising-database-updates-in-fastapi-application-to-prevent-race-conditions-eda349b5a68e
        current_user.credit = User.credit - (
            request.volume * CURRENCIES_PRICE_MAPPING[request.name]
        )

        transaction = Transaction(
            user_id=current_user.id,
            currency=request.name,
            price=CURRENCIES_PRICE_MAPPING[request.name],
            volume=request.volume,
            is_settled=False,
        )
        session.add(transaction)

        session.commit()
        session.refresh(current_user)
        session.refresh(transaction)

        # NOTE: any exception furthure here results in data inconsistency
        with contextlib.suppress(Exception):
            background_tasks.add_task(buy_from_exchange)

        return Response(status_code=status.HTTP_202_ACCEPTED)

    except Exception as exc:
        logger.exception(exc)
        session.rollback()

    raise HTTPException(status_code=400, detail="Insufficient credit")
