from datetime import datetime

import pytest

from app.models import Transaction, TransactionType
from app.transaction_service.schemas import (
    TransactionReportSchema,
    TransactionSchema,
)
from app.transaction_service.views import (
    create_transaction_view,
    get_transactions_view,
    transaction_reports,
    transactions,
)

user_transaction = {
    'user_1': [
        Transaction(100, TransactionType.DEPOSIT, datetime.now()),
        Transaction(300, TransactionType.WITHDRAWAL, datetime.now()),
        Transaction(1000, TransactionType.DEPOSIT, datetime.now()),
    ],
    'user_2': [
        Transaction(100, TransactionType.WITHDRAWAL, datetime.now()),
    ],
    'user_1000': [
        Transaction(1000, TransactionType.DEPOSIT, datetime.now()),
        Transaction(1000, TransactionType.DEPOSIT, datetime.now()),
    ],
}


transaction_params = [
    pytest.param(1, user_transaction['user_1'], id='three_transactions'),
    pytest.param(2, user_transaction['user_2'], id='one_withdrawal'),
    pytest.param(1000, user_transaction['user_1000'], id='user_1000'),
]


@pytest.mark.parametrize(
    'user_id, amount, transaction_type',
    [
        pytest.param(1, 100, TransactionType.DEPOSIT, id='Deposit'),
        pytest.param(1, 300, TransactionType.WITHDRAWAL, id='Withdrawal'),
        pytest.param(2, 100, TransactionType.DEPOSIT, id='Deposit_user_2'),
        pytest.param(1000, 1000, TransactionType.WITHDRAWAL,
                     id='Withdrawal_user_1000'),
    ],
)
def test_create_transaction(user_id, amount, transaction_type):
    create_transaction_view(
        TransactionSchema(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
        ),
    )

    assert list(transactions) == [user_id]
    assert len(transactions[user_id]) == 1
    transaction = transactions[user_id][0]
    assert transaction.amount == amount
    assert transaction.transaction_type == transaction_type


def test_create_many_transactions():
    create_transaction_view(
        TransactionSchema(
            user_id=1,
            amount=100,
            transaction_type=TransactionType.DEPOSIT,
        ),
    )
    create_transaction_view(
        TransactionSchema(
            user_id=1,
            amount=300,
            transaction_type=TransactionType.WITHDRAWAL,
        ),
    )
    create_transaction_view(
        TransactionSchema(
            user_id=1,
            amount=1000,
            transaction_type=TransactionType.DEPOSIT,
        ),
    )

    create_transaction_view(
        TransactionSchema(
            user_id=2,
            amount=100,
            transaction_type=TransactionType.DEPOSIT,
        ),
    )
    create_transaction_view(
        TransactionSchema(
            user_id=1000,
            amount=1000,
            transaction_type=TransactionType.WITHDRAWAL,
        ),
    )

    assert list(transactions) == [1, 2, 1000]  # 1, 2, 1000 - id users
    assert len(transactions[1]) == 3
    assert len(transactions[2]) == 1
    assert len(transactions[1000]) == 1


@pytest.mark.parametrize(
    'user_id, existing_transactions',
    transaction_params,
)
def test_get_transactions_found_all(user_id, existing_transactions):
    transactions[user_id] = []
    for transaction in existing_transactions:
        transactions[user_id].append(transaction)

    user_transactions = get_transactions_view(TransactionReportSchema(
        user_id=user_id,
        date_start=datetime(2024, 1, 1),
        date_end=datetime(2124, 1, 1),
    ))

    assert user_transactions == existing_transactions


@pytest.mark.parametrize(
    'user_id, existing_transactions',
    transaction_params,
)
def test_get_transactions_not_found(user_id, existing_transactions):
    transactions[user_id] = []
    for transaction in existing_transactions:
        transactions[user_id].append(transaction)

    user_transactions = get_transactions_view(TransactionReportSchema(
        user_id=user_id,
        date_start=datetime(1000, 1, 1),
        date_end=datetime(1000, 1, 1),
    ))

    assert not user_transactions


@pytest.mark.parametrize(
    'user_id, existing_transactions',
    transaction_params,
)
def test_get_transaction_report(user_id, existing_transactions):
    transactions[user_id] = []
    for transaction in existing_transactions:
        transactions[user_id].append(transaction)

    get_transactions_view(
        TransactionReportSchema(
            user_id=user_id,
            date_start=datetime(2024, 1, 1),
            date_end=datetime(2124, 1, 1),
        ),
    )

    assert user_id in transaction_reports
    assert len(transaction_reports[user_id]) == 1
    report = transaction_reports[user_id][0]

    assert report.date_start == datetime(2024, 1, 1)
    assert report.date_end == datetime(2124, 1, 1)
    assert report.transactions == existing_transactions


def test_get_transaction_wrong_user(add_user_1_transactions):
    with pytest.raises(KeyError):
        get_transactions_view(TransactionReportSchema(
            user_id=2,
            date_start=datetime(2024, 1, 1),
            date_end=datetime(2124, 1, 1)),
        )
