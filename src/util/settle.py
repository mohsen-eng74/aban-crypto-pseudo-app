from __future__ import annotations

import asyncio
import logging

from sqlmodel import Session, select

from src.constant import MINIMUM_ALLOWED_EXCHANGE_VALUE
from src.extension import engine
from src.model import Transaction

logger = logging.getLogger(__name__)


async def buy_from_exchange() -> None:
    try:
        with Session(engine) as session:
            transactions = session.exec(  # select transactions with lock
                select(Transaction)
                .where(Transaction.is_settled == False)
                .with_for_update()
            ).all()

            if (
                sum(transaction.value for transaction in transactions)
                >= MINIMUM_ALLOWED_EXCHANGE_VALUE
            ):
                logger.info(rf"purchasing from exchange: {transactions=}")
                await asyncio.sleep(5)  # simulating an I/O job

                for transaction in transactions:
                    transaction.is_settled = True
                    session.add(transaction)

                session.commit()

    except Exception as exc:
        logger.exception(exc)
        session.rollback()
