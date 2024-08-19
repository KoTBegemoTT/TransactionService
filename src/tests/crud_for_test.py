from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import TransactionReport, UserTransaction


async def get_user_transactions(
    user_id: int,
    session: AsyncSession,
) -> list[UserTransaction]:
    """Получение списка транзакций пользователя."""
    transactions = await session.scalars(
        select(UserTransaction)
        .where(UserTransaction.user_id == user_id),
    )

    return list(transactions)


async def get_user_reports(
    user_id: int,
    session: AsyncSession,
) -> list[TransactionReport]:
    """Получение списка транзакций пользователя."""
    reports = await session.scalars(
        select(TransactionReport)
        .where(TransactionReport.user_id == user_id),
    )

    return list(reports)


async def get_report_transactions(
    report_id: int,
    session: AsyncSession,
) -> list[UserTransaction]:
    """Получение списка транзакций связанного с отчётом."""
    report = await session.scalar(
        select(TransactionReport)
        .where(TransactionReport.id == report_id)
        .options(
            selectinload(TransactionReport.transactions),
        ),
    )

    return report.transactions
