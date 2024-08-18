from datetime import datetime

from sqlalchemy import select

from app.db.models import UserTransaction, TransactionReport, TransactionType
from app.transaction_service.schemas import (
    TransactionOutSchema,
    TransactionReportSchema,
    TransactionSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession

transaction_report_cache: dict[int, dict[str, TransactionReport]] = {}
transaction_type_id_cache: dict[str, int] = {}


async def create_transation_type(
    name: str,
    session: AsyncSession,
) -> TransactionType:
    """Создание типа транзакции."""
    transaction_type = TransactionType(name=name)
    session.add(transaction_type)
    await session.commit()
    return transaction_type


async def get_transation_type_by_name(
    name: str,
    session: AsyncSession
) -> TransactionType | None:
    """Получение типа транзакции по имени."""
    return await session.scalar(
        select(TransactionType)
        .where(TransactionType.name == name)
    )


async def get_or_create_transaction_type(
    name: str,
    session: AsyncSession,
) -> TransactionType:
    """Получение или создание типа транзакции."""
    transaction_type = await get_transation_type_by_name(name, session)

    if transaction_type:
        return transaction_type

    transaction_type = await create_transation_type(
        name=name,
        session=session,
    )

    return transaction_type


async def get_or_create_transaction_type_id(
    type_name: str,
    session: AsyncSession,
) -> int:
    """Получение id типа транзакции."""
    if type_name in transaction_type_id_cache:
        return transaction_type_id_cache[type_name]

    transaction_type = await get_or_create_transaction_type(type_name, session)
    transaction_type_id_cache[type_name] = transaction_type.id

    return transaction_type.id


async def create_user_transaction(
    user_id: int,
    amount: int,
    transaction_type_id: int,
    session: AsyncSession,
) -> UserTransaction:
    """Создание новой транзакции."""

    transaction_bd = UserTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type_id=transaction_type_id,
        date=datetime.now(),
    )
    session.add(transaction_bd)
    await session.commit()

    return transaction_bd


async def create_transaction_view(
    transaction: TransactionSchema,
    session: AsyncSession,
) -> None:
    """Создание новой транзакции."""
    transaction_type_id = await get_or_create_transaction_type_id(
        transaction.transaction_type.value,
        session,
    )
    
    await create_user_transaction(
        transaction.user_id,
        transaction.amount,
        transaction_type_id,
        session,
    )


def concat_date(date_start: datetime, date_end: datetime) -> str:
    """Соединяет даты в строку."""
    return f'{date_start.isoformat()} - {date_end.isoformat()}'


async def save_report(
    report: TransactionReportSchema,
    user_transactions: list[TransactionOutSchema],
) -> None:
    """Сохранение отчета о транзакциях."""
    if report.user_id not in transaction_reports:
        transaction_reports[report.user_id] = {}

    report_dates = concat_date(report.date_start, report.date_end)
    transaction_reports[report.user_id][report_dates] = TransactionReport(
        report.date_start,
        report.date_end,
        user_transactions,
    )


async def found_report(
    report: TransactionReportSchema,
) -> TransactionReport | None:
    """Поиск отчета о транзакциях."""
    if report.user_id not in transaction_reports:
        return None

    user_reports = transaction_reports[report.user_id]
    report_dates = concat_date(report.date_start, report.date_end)
    return user_reports.get(report_dates, None)


async def get_transactions_view(
    report: TransactionReportSchema,
) -> list[TransactionOutSchema]:
    """Получение списка транзакций."""
    existing_report = await found_report(report)
    if existing_report:
        return existing_report.transactions

    user_transactions = []
    for transaction in transactions[report.user_id]:
        if report.date_start < transaction.date < report.date_end:
            user_transactions.append(transaction)

    await save_report(report, user_transactions)

    return user_transactions
