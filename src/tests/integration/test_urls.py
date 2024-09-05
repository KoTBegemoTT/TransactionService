from datetime import datetime

import pytest
from fastapi import status

from app.transaction_service.views import transaction_report_cache
from tests.crud_for_test import get_user_transactions


@pytest.mark.parametrize(
    'amount, transaction_type',
    [
        pytest.param(100, 'Пополнение', id='Deposit'),
        pytest.param(300, 'Снятие', id='Withdrawal'),
    ],
)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db', 'clear_cache')
async def test_create_transaction(
    ac, user, amount, transaction_type, db_helper,
):
    response = await ac.post(
        'api/transactions/create/',
        json={
            'user_id': user.id,
            'amount': amount,
            'transaction_type': transaction_type,
        },
    )

    async with db_helper.session_factory() as session:
        transactions = await get_user_transactions(user.id, session)

    assert response.status_code == status.HTTP_201_CREATED
    assert len(transactions) == 1
    transaction = transactions[0]
    assert transaction.amount == amount
    assert transaction.user_id == user.id


@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db', 'clear_cache')
async def test_get_transactions(ac, user_and_transactions):
    user, transactions = user_and_transactions

    response = await ac.post(
        'api/transactions/report/',
        json={
            'user_id': user.id,
            'date_start': datetime(2024, 1, 1).isoformat(),
            'date_end': datetime(2124, 1, 1).isoformat(),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()) == len(transactions)
    assert len(transaction_report_cache) == 1


@pytest.mark.asyncio
async def test_check_ready(ac):
    response = await ac.get('api/healthz/ready/')

    assert response.status_code == status.HTTP_200_OK
