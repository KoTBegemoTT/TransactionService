from datetime import datetime
from unittest.mock import Mock

import pytest
import sqlalchemy

from app.transaction_service.schemas import (
    TransactionOutSchema,
    TransactionReportSchema,
    TransactionSchema,
    TransactionTypeSchema,
)
from app.transaction_service.views import (
    create_transaction_view,
    get_report_key,
    get_transactions_view,
)
from app.utils import json_nested_dump
from tests.crud_for_test import (
    get_report_transactions,
    get_user_reports,
    get_user_transactions,
)


@pytest.mark.parametrize(
    'amount, transaction_type',
    [
        pytest.param(100, TransactionTypeSchema.DEPOSIT, id='Deposit'),
        pytest.param(300, TransactionTypeSchema.WITHDRAWAL, id='Withdrawal'),
    ],
)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db')
async def test_create_transaction(
    user, amount, transaction_type, db_helper, redis_mock,
):
    async with db_helper.session_factory() as session:
        await create_transaction_view(
            TransactionSchema(
                user_id=1,
                amount=amount,
                transaction_type=transaction_type,
            ),
            session,
            redis_mock,
        )
        transactions = await get_user_transactions(user.id, session)

    assert len(transactions) == 1
    transaction = transactions[0]
    assert transaction.amount == amount
    assert transaction.user_id == user.id


@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db')
async def test_create_many_transactions(user, db_helper, redis_mock):
    async with db_helper.session_factory() as session:
        for _ in range(5):
            await create_transaction_view(
                TransactionSchema(
                    user_id=user.id,
                    amount=100,
                    transaction_type=TransactionTypeSchema.DEPOSIT,
                ),
                session,
                redis_mock,
            )

        transactions = await get_user_transactions(user.id, session)

    assert len(transactions) == 5


@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_get_transactions_found_all(
    user_and_transactions, db_helper, redis_mock,
):
    user, transactions_out = user_and_transactions

    async with db_helper.session_factory() as session:
        user_transactions = await get_transactions_view(
            TransactionReportSchema(
                user_id=user.id,
                date_start=datetime(2024, 1, 1),
                date_end=datetime(2124, 1, 1),
            ),
            session,
            redis_mock,
        )

    assert user_transactions == transactions_out


@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_get_transactions_not_found(
    user_and_transactions, db_helper, redis_mock,
):
    user, transactions_out = user_and_transactions

    async with db_helper.session_factory() as session:
        user_transactions = await get_transactions_view(
            TransactionReportSchema(
                user_id=user.id,
                date_start=datetime(1000, 1, 1),
                date_end=datetime(1000, 1, 1),
            ),
            session,
            redis_mock,
        )

    assert not user_transactions


@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_get_transaction_report_exists_in_cache(db_helper, redis_mock):
    cashed_transactions = [
        TransactionOutSchema(
            user_id=1,
            amount=100,
            transaction_type_id=1,
            date=datetime.now(),
        ),
        TransactionOutSchema(
            user_id=1,
            amount=300,
            transaction_type_id=2,
            date=datetime.now(),
        ),
    ]

    redis_mock.get_report_transaction = Mock(
        return_value=json_nested_dump(cashed_transactions),
    )

    async with db_helper.session_factory() as session:
        user_transactions = await get_transactions_view(
            TransactionReportSchema(
                user_id=1,
                date_start=datetime(2024, 1, 1),
                date_end=datetime(2124, 1, 1),
            ),
            session,
            redis_mock,
        )

    restored_transactions = [
        TransactionOutSchema.model_validate(t) for t in user_transactions
    ]
    assert restored_transactions == cashed_transactions


@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_get_transaction_report(
    user_and_transactions, db_helper, redis_mock,
):
    user, transactions_out = user_and_transactions

    async with db_helper.session_factory() as session:
        await get_transactions_view(
            TransactionReportSchema(
                user_id=user.id,
                date_start=datetime(2024, 1, 1),
                date_end=datetime(2124, 1, 1),
            ),
            session,
            redis_mock,
        )

        reports = await get_user_reports(user.id, session)
        report_transactions = await get_report_transactions(user.id, session)

    assert len(redis_mock.get_cash()) == 1
    assert len(reports) == 1
    report = reports[0]

    assert report.date_start == datetime(2024, 1, 1)
    assert report.date_end == datetime(2124, 1, 1)
    assert len(report_transactions) == len(transactions_out)


@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db')
async def test_get_transaction_wrong_user(db_helper, redis_mock):
    async with db_helper.session_factory() as session:
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            await get_transactions_view(
                TransactionReportSchema(
                    user_id=1000,
                    date_start=datetime(2024, 1, 1),
                    date_end=datetime(2124, 1, 1),
                ),
                session,
                redis_mock,
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user_id, date_start, date_end, concated',
    [
        pytest.param(
            1,
            datetime(2024, 1, 1),
            datetime(2124, 1, 1),
            '1_2024-01-01T00:00:00_2124-01-01T00:00:00',
            id='big_range',
        ),
        pytest.param(
            2,
            datetime(2024, 1, 1),
            datetime(2024, 1, 1),
            '2_2024-01-01T00:00:00_2024-01-01T00:00:00',
            id='small_range',
        ),
    ],
)
async def test_get_report_key(user_id, date_start, date_end, concated):
    assert get_report_key(user_id, date_start, date_end) == concated
