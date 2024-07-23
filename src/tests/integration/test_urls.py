from datetime import datetime

import pytest
from fastapi import status

from app.models import TransactionType
from app.transaction_service.schemas import TransactionSchema
from app.transaction_service.views import transaction_reports, transactions

user_transaction = {
    1:
    [
        TransactionSchema(user_id=1, amount=100,
                          transaction_type=TransactionType.DEPOSIT),
        TransactionSchema(user_id=1, amount=300,
                          transaction_type=TransactionType.WITHDRAWAL),
        TransactionSchema(user_id=1, amount=1000,
                          transaction_type=TransactionType.DEPOSIT),
    ],
    2:
    [
        TransactionSchema(user_id=2, amount=100,
                          transaction_type=TransactionType.DEPOSIT),
    ],
    1000:
    [
        TransactionSchema(user_id=1000, amount=1000,
                          transaction_type=TransactionType.WITHDRAWAL),
    ],
}


@pytest.mark.parametrize(
    'user_id, amount, transaction_type',
    [
        pytest.param(1, 100, 'Пополнение', id='Deposit'),
        pytest.param(1, 300, 'Снятие', id='Withdrawal'),
        pytest.param(2, 100, 'Пополнение', id='Deposit_user_2'),
        pytest.param(1000, 1000, 'Снятие',
                     id='Withdrawal_user_1000'),
    ],
)
def test_create_transaction(test_client, user_id, amount, transaction_type):
    response = test_client.post(
        '/transactions/create',
        json={
            'user_id': user_id,
            'amount': amount,
            'transaction_type': transaction_type,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert list(transactions) == [user_id]
    assert len(transactions[user_id]) == 1
    transaction = transactions[user_id][0]
    assert transaction.amount == amount
    assert transaction.transaction_type == TransactionType(transaction_type)


@pytest.mark.parametrize(
    'user_transaction, report_user_id',
    [
        pytest.param(user_transaction, 1, id='user_1'),
        pytest.param(user_transaction, 2, id='user_2'),
        pytest.param(user_transaction, 1000, id='user_1000'),
    ],
)
def test_get_transactions(test_client, user_transaction, report_user_id):
    for new_transactions in user_transaction.values():
        for transaction in new_transactions:
            test_client.post(
                '/transactions/create',
                json={
                    'user_id': transaction.user_id,
                    'amount': transaction.amount,
                    'transaction_type': transaction.transaction_type.value,
                },
            )

    response = test_client.post(
        '/transactions/report',
        json={
            'user_id': report_user_id,
            'date_start': datetime(2024, 1, 1).isoformat(),
            'date_end': datetime(2124, 1, 1).isoformat(),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()) == len(user_transaction[report_user_id])

    assert len(transaction_reports) == 1
    report = transaction_reports[report_user_id][0]
    assert report.date_start == datetime(2024, 1, 1)
    assert report.date_end == datetime(2124, 1, 1)
