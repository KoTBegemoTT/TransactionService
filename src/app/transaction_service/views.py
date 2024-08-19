from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import TransactionReport, TransactionType, UserTransaction
from app.transaction_service.schemas import (
    TransactionOutSchema,
    TransactionReportSchema,
    TransactionSchema,
)

transaction_report_cache: dict[str, list[TransactionOutSchema]] = {}
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
    session: AsyncSession,
) -> TransactionType | None:
    """Получение типа транзакции по имени."""
    return await session.scalar(
        select(TransactionType)
        .where(TransactionType.name == name),
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
    return f'{date_start.isoformat()}_{date_end.isoformat()}'


def get_report_key(
    user_id: int, date_start: datetime, date_end: datetime,
) -> str:
    """Соединяет данные в строку."""
    dates = concat_date(date_start, date_end)
    return f'{user_id}_{dates}'


async def create_report(
    user_id: int,
    date_start: datetime,
    date_end: datetime,
    session: AsyncSession,
) -> TransactionReport:
    """Создание отчета о транзакциях."""
    report = TransactionReport(
        user_id=user_id,
        date_start=date_start,
        date_end=date_end,
    )
    session.add(report)
    await session.commit()
    return report


async def create_report_transaction_relations(
    report_id: int,
    user_transactions: list[UserTransaction],
    session: AsyncSession,
) -> None:
    """Сохранение транзакций."""
    report = await session.scalar(
        select(TransactionReport)
        .where(TransactionReport.id == report_id)
        .options(
            selectinload(TransactionReport.transactions),
        ),
    )
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Отчет не найден')

    report.transactions.extend(user_transactions)

    await session.commit()


async def save_report(
    report_in: TransactionReportSchema,
    user_transactions: list[UserTransaction],
    session: AsyncSession,
) -> None:
    """Сохранение отчета о транзакциях."""
    report = await create_report(
        report_in.user_id,
        report_in.date_start,
        report_in.date_end,
        session,
    )

    await create_report_transaction_relations(
        report.id, user_transactions, session,
    )


async def get_user_transactions_in_period(
    user_id: int,
    date_start: datetime,
    date_end: datetime,
    session: AsyncSession,
) -> list[UserTransaction]:
    """Получение списка транзакций за период."""
    transactions = await session.scalars(
        select(UserTransaction)
        .where(UserTransaction.user_id == user_id)
        .where(UserTransaction.date.between(date_start, date_end)),
    )

    return list(transactions)


async def get_trasactions_form_cache(
    report: TransactionReportSchema,
) -> list[TransactionOutSchema] | None:
    """Поиск отчета о транзакциях."""
    report_key = get_report_key(
        report.user_id, report.date_start, report.date_end,
    )
    return transaction_report_cache.get(report_key, None)


async def save_report_cache(
    report: TransactionReportSchema,
    user_transactions: list[TransactionOutSchema],
) -> None:
    """Сохранение отчета о транзакциях."""
    report_key = get_report_key(
        report.user_id, report.date_start, report.date_end,
    )
    transaction_report_cache[report_key] = user_transactions


async def get_transactions_view(
    report: TransactionReportSchema,
    session: AsyncSession,
) -> list[TransactionOutSchema]:
    """Получение списка транзакций."""
    cashed_transactions = await get_trasactions_form_cache(report)
    if cashed_transactions is not None:
        return cashed_transactions

    user_transactions_orm = await get_user_transactions_in_period(
        report.user_id,
        report.date_start,
        report.date_end,
        session,
    )

    await save_report(report, user_transactions_orm, session)
    user_transactions_out = [
        TransactionOutSchema.model_validate(transaction)
        for transaction in user_transactions_orm
    ]
    await save_report_cache(report, user_transactions_out)

    return user_transactions_out
