import pytest
from app.logic import TransactionService, transactions, transaction_reports
from datetime import datetime


class TestCreateTransaction:
    @pytest.mark.parametrize(
        "user_id, amount, transaction_type",
        [
            (1, 100, "Пополнение"),
            (1, 300, "Снятие"),
            (1, 1000, "Пополнение"),
            (2, 100, "Пополнение"),
            (1000, 1000, "Снятие"),
        ],
    )
    def test_create_transaction(self, user_id, amount, transaction_type):
        TransactionService.create_transaction(user_id, amount, transaction_type)

        assert list(transactions) == [user_id]
        assert len(transactions[user_id]) == 1
        transaction = transactions[user_id][0]
        assert transaction.amount == amount
        assert transaction.transaction_type.value == transaction_type

    def test_create_many_transactions(self):
        TransactionService.create_transaction(1, 100, "Пополнение")
        TransactionService.create_transaction(1, 300, "Снятие")
        TransactionService.create_transaction(1, 1000, "Пополнение")

        TransactionService.create_transaction(2, 100, "Пополнение")
        TransactionService.create_transaction(1000, 1000, "Снятие")

        assert list(transactions) == [1, 2, 1000]  # 1, 2, 1000 - id users
        assert len(transactions[1]) == 3
        assert len(transactions[2]) == 1
        assert len(transactions[1000]) == 1

    @pytest.mark.parametrize(
        "user_id, amount, transaction_type, error",
        [
            ("1", 100, "Снятие", TypeError),
            (1, 100, "Нет типа", ValueError),
        ],
    )
    def test_create_transaction_fail(self, user_id, amount, transaction_type, error):
        with pytest.raises(error):
            TransactionService.create_transaction(user_id, amount, transaction_type)


class TestGetTransaction:
    def test_get_transactions(self, add_user_1_transactions):
        user_transactions = TransactionService.get_transactions(
            user_id=1, date_start=datetime(2024, 1, 1), date_end=datetime(2124, 1, 1)
        )

        assert len(user_transactions) == 3

    def test_get_transaction_report(self, add_user_1_transactions):
        TransactionService.get_transactions(
            user_id=1, date_start=datetime(2024, 1, 1), date_end=datetime(2124, 1, 1)
        )

        report = transaction_reports[0]

        assert len(report.transactions) == 3

        assert report.user_id == 1
        assert report.date_start == datetime(2024, 1, 1)
        assert report.date_end == datetime(2124, 1, 1)

    def test_get_transaction_wrong_user(self, add_user_1_transactions):
        with pytest.raises(KeyError):
            TransactionService.get_transactions(
                user_id=2,
                date_start=datetime(2024, 1, 1),
                date_end=datetime(2124, 1, 1),
            )

    @pytest.mark.parametrize(
        "user_id, date_start, date_end",
        [
            (1, "NotDate", datetime(2124, 1, 1)),
            (1, datetime(2024, 1, 1), "NotDate"),
        ],
    )
    def test_get_transaction_wrong_date(
        self, user_id, date_start, date_end, add_user_1_transactions
    ):
        with pytest.raises(TypeError):
            TransactionService.get_transactions(
                user_id=user_id, date_start=date_start, date_end=date_end
            )
