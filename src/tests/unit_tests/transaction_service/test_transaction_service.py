import pytest
from app.logic import TransactionService, transactions, transaction_reports
from datetime import datetime

from app.models import Transaction, TransactionType

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


class TestCreateTransaction:
    @pytest.mark.parametrize(
        'user_id, amount, transaction_type',
        [
            pytest.param(1, 100, 'Пополнение', id='Deposit'),
            pytest.param(1, 300, 'Снятие', id='Withdrawal'),
            pytest.param(2, 100, 'Пополнение', id='Deposit_user_2'),
            pytest.param(1000, 1000, 'Снятие', id='Withdrawal_user_1000'),
        ],
    )
    def test_create_transaction(self, user_id, amount, transaction_type):
        TransactionService.create_transaction(
            user_id, amount, transaction_type)

        assert list(transactions) == [user_id]
        assert len(transactions[user_id]) == 1
        transaction = transactions[user_id][0]
        assert transaction.amount == amount
        assert transaction.transaction_type.value == transaction_type

    def test_create_many_transactions(self):
        TransactionService.create_transaction(1, 100, 'Пополнение')
        TransactionService.create_transaction(1, 300, 'Снятие')
        TransactionService.create_transaction(1, 1000, 'Пополнение')

        TransactionService.create_transaction(2, 100, 'Пополнение')
        TransactionService.create_transaction(1000, 1000, 'Снятие')

        assert list(transactions) == [1, 2, 1000]  # 1, 2, 1000 - id users
        assert len(transactions[1]) == 3
        assert len(transactions[2]) == 1
        assert len(transactions[1000]) == 1

    @pytest.mark.parametrize(
        'user_id, amount, transaction_type, error',
        [
            pytest.param('1', 100, 'Снятие', TypeError, id='wrong_user_id'),
            pytest.param(
                1, 100, 'Нет типа', ValueError, id='wrong_transaction_type',
            ),
        ],
    )
    def test_create_transaction_fail(
        self, user_id, amount, transaction_type, error,
    ):
        with pytest.raises(error):
            TransactionService.create_transaction(
                user_id, amount, transaction_type)


class TestGetTransaction:
    @pytest.mark.parametrize(
        'user_id, existing_transactions',
        transaction_params,
    )
    def test_get_transactions_found_all(self, user_id, existing_transactions):
        transactions[user_id] = []
        for transaction in existing_transactions:
            transactions[user_id].append(transaction)

        user_transactions = TransactionService.get_transactions(
            user_id=user_id,
            date_start=datetime(2024, 1, 1),
            date_end=datetime(2124, 1, 1),
        )

        assert user_transactions == existing_transactions

    @pytest.mark.parametrize(
        'user_id, existing_transactions',
        transaction_params,
    )
    def test_get_transactions_not_found(self, user_id, existing_transactions):
        transactions[user_id] = []
        for transaction in existing_transactions:
            transactions[user_id].append(transaction)

        user_transactions = TransactionService.get_transactions(
            user_id=user_id,
            date_start=datetime(1000, 1, 1),
            date_end=datetime(1000, 1, 1),
        )

        assert not user_transactions

    @pytest.mark.parametrize(
        'user_id, existing_transactions',
        transaction_params,
    )
    def test_get_transaction_report(self, user_id, existing_transactions):
        transactions[user_id] = []
        for transaction in existing_transactions:
            transactions[user_id].append(transaction)

        TransactionService.get_transactions(
            user_id=user_id,
            date_start=datetime(2024, 1, 1),
            date_end=datetime(2124, 1, 1),
        )

        assert len(transaction_reports) == 1
        report = transaction_reports[0]

        assert report.user_id == user_id
        assert report.date_start == datetime(2024, 1, 1)
        assert report.date_end == datetime(2124, 1, 1)
        assert report.transactions == existing_transactions

    def test_get_transaction_wrong_user(self, add_user_1_transactions):
        with pytest.raises(KeyError):
            TransactionService.get_transactions(
                user_id=2,
                date_start=datetime(2024, 1, 1),
                date_end=datetime(2124, 1, 1),
            )

    @pytest.mark.parametrize(
        'user_id, date_start, date_end',
        [
            pytest.param(
                1, 'NotDate', datetime(2124, 1, 1), id='wrong_date_start',
            ),
            pytest.param(
                1, datetime(2024, 1, 1), 'NotDate', id='wrong_date_end',
            ),
        ],
    )
    def test_get_transaction_wrong_date(
        self, user_id, date_start, date_end, add_user_1_transactions,
    ):
        with pytest.raises(TypeError):
            TransactionService.get_transactions(
                user_id=user_id, date_start=date_start, date_end=date_end,
            )
