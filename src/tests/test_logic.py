from app.logic import TransactionService, transactions, transaction_reports
from datetime import datetime


def setup_function():
    transactions.clear()
    transaction_reports.clear()


def test_create_transaction():
    setup_function()
    TransactionService.create_transaction(1, 100, "Пополнение")
    transaction = transactions[1][0]
    assert len(transactions[1]) == 1
    assert transaction.amount == 100
    assert transaction.transaction_type == "Пополнение"


def test_get_transactions():
    setup_function()
    TransactionService.create_transaction(1, 100, "Пополнение")
    TransactionService.create_transaction(1, 300, "Снятие")
    TransactionService.create_transaction(1, 1000, "Пополнение")
    user_transactions = TransactionService.get_transactions(
        user_id=1, date_start=datetime(2024, 1, 1), date_end=datetime(2124, 1, 1)
    )

    assert len(user_transactions) == 3


def test_get_transaction_report():
    setup_function()
    TransactionService.create_transaction(1, 100, "Пополнение")
    TransactionService.create_transaction(1, 300, "Снятие")
    TransactionService.create_transaction(1, 1000, "Пополнение")
    TransactionService.get_transactions(
        user_id=1, date_start=datetime(2024, 1, 1), date_end=datetime(2124, 1, 1)
    )

    report = transaction_reports[0]

    assert len(report.transactions) == 3

    assert report.user_id == 1
    assert report.date_start == datetime(2024, 1, 1)
    assert report.date_end == datetime(2124, 1, 1)
