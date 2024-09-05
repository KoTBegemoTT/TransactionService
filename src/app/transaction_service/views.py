from datetime import datetime

from fastapi import HTTPException, status
from opentracing import global_tracer
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
    with global_tracer().start_active_span('create_transation_type') as scope:
        scope.span.set_tag('name', name)
        transaction_type = TransactionType(name=name)
        session.add(transaction_type)
        await session.commit()

        scope.span.set_tag('id created transaction_type', transaction_type.id)
        return transaction_type


async def get_transation_type_by_name(
    name: str,
    session: AsyncSession,
) -> TransactionType | None:
    """Получение типа транзакции по имени."""
    with global_tracer().start_active_span('get_transation_type_by_name'):
        return await session.scalar(
            select(TransactionType)
            .where(TransactionType.name == name),
        )


async def get_or_create_transaction_type(
    name: str,
    session: AsyncSession,
) -> TransactionType:
    """Получение или создание типа транзакции."""
    with global_tracer().start_active_span('get_or_create_transaction_type') as scope:  # noqa: E501
        scope.span.set_tag('name', name)
        transaction_type = await get_transation_type_by_name(name, session)

        if transaction_type:
            scope.span.set_tag(
                'transaction_type_id founded in db',
                transaction_type.id,
            )
            return transaction_type

        transaction_type = await create_transation_type(
            name=name,
            session=session,
        )

        scope.span.set_tag('transaction_type_id created', transaction_type.id)

        return transaction_type


async def get_or_create_transaction_type_id(
    type_name: str,
    session: AsyncSession,
) -> int:
    """Получение id типа транзакции."""
    with global_tracer().start_active_span('get_or_create_transaction_type_id') as scope:  # noqa: E501
        scope.span.set_tag('type_name', type_name)
        if type_name in transaction_type_id_cache:
            type_id = transaction_type_id_cache[type_name]
            scope.span.set_tag('transaction_type_id from cache', type_id)
            return type_id

        transaction_type = await get_or_create_transaction_type(
            type_name,
            session,
        )
        transaction_type_id_cache[type_name] = transaction_type.id

        scope.span.set_tag(
            'transaction_type_id saved in cache',
            transaction_type.id,
        )
        return transaction_type.id


async def create_user_transaction(
    user_id: int,
    amount: int,
    transaction_type_id: int,
    session: AsyncSession,
) -> UserTransaction:
    """Создание новой транзакции."""
    with global_tracer().start_active_span('create_user_transaction') as scope:
        scope.span.set_tag('user_id', user_id)
        scope.span.set_tag('amount', amount)
        scope.span.set_tag('transaction_type_id', transaction_type_id)
        transaction_bd = UserTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type_id=transaction_type_id,
            date=datetime.now(),
        )
        session.add(transaction_bd)
        await session.commit()

        scope.span.set_tag('id created transaction', transaction_bd.id)
        return transaction_bd


async def create_transaction_view(
    transaction: TransactionSchema,
    session: AsyncSession,
) -> None:
    """Создание новой транзакции."""
    with global_tracer().start_active_span('create_transaction_view') as scope:
        scope.span.set_tag('transaction', str(transaction))
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
    with global_tracer().start_active_span('create_report') as scope:
        scope.span.set_tag('user_id', user_id)
        report = TransactionReport(
            user_id=user_id,
            date_start=date_start,
            date_end=date_end,
        )
        session.add(report)
        await session.commit()
        scope.span.set_tag('id created report', report.id)
        return report


async def create_report_transaction_relations(
    report_id: int,
    user_transactions: list[UserTransaction],
    session: AsyncSession,
) -> None:
    """Сохранение транзакций."""
    with global_tracer().start_active_span('create_report_transaction_relations') as scope:  # noqa: E501
        scope.span.set_tag('report_id', report_id)

        report = await session.scalar(
            select(TransactionReport)
            .where(TransactionReport.id == report_id)
            .options(
                selectinload(TransactionReport.transactions),
            ),
        )
        if report is None:
            scope.span.set_tag('error', 'Отчет не найден')
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'Отчет не найден')

        report.transactions.extend(user_transactions)

        await session.commit()


async def save_report(
    report_in: TransactionReportSchema,
    user_transactions: list[UserTransaction],
    session: AsyncSession,
) -> None:
    """Сохранение отчета о транзакциях."""
    with global_tracer().start_active_span('save_report') as scope:
        scope.span.set_tag('report_in', str(report_in))
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
    with global_tracer().start_active_span('get_user_transactions_in_period') as scope:  # noqa: E501
        scope.span.set_tag('user_id', user_id)
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
    with global_tracer().start_active_span('get_trasactions_form_cache') as scope:  # noqa: E501
        report_key = get_report_key(
            report.user_id,
            report.date_start,
            report.date_end,
        )

        scope.span.set_tag('report_key', report_key)
        return transaction_report_cache.get(report_key, None)


async def save_report_cache(
    report: TransactionReportSchema,
    user_transactions: list[TransactionOutSchema],
) -> None:
    """Сохранение отчета о транзакциях."""
    with global_tracer().start_active_span('save_report_cache'):
        report_key = get_report_key(
            report.user_id, report.date_start, report.date_end,
        )
        transaction_report_cache[report_key] = user_transactions


async def get_transactions_view(
    report: TransactionReportSchema,
    session: AsyncSession,
) -> list[TransactionOutSchema]:
    """Получение списка транзакций."""
    with global_tracer().start_active_span('get_transactions_view') as scope:
        scope.span.set_tag('report', str(report))
        cashed_transactions = await get_trasactions_form_cache(report)
        if cashed_transactions is not None:
            scope.span.set_tag('cashed_transactions', str(cashed_transactions))
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

        scope.span.set_tag('user_transactions_out', str(user_transactions_out))
        await save_report_cache(report, user_transactions_out)

        return user_transactions_out
