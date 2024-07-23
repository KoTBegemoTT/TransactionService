from datetime import datetime

from app.models import Transaction, TransactionReport
from app.transaction_service.schemas import (
    TransactionReportSchema,
    TransactionSchema,
)

transactions: dict[int, list[Transaction]] = {}
transaction_reports: dict[int, list[TransactionReport]] = {}


def create_transaction_view(transaction: TransactionSchema) -> None:
    """Создание новой транзакции."""
    transaction_bd = Transaction(
        transaction.amount, transaction.transaction_type, datetime.now(),
    )
    if transaction.user_id not in transactions:
        transactions[transaction.user_id] = [transaction_bd]
    else:
        transactions[transaction.user_id].append(transaction_bd)


def save_report(
    report: TransactionReportSchema,
    user_transactions: list[Transaction],
) -> None:
    """Сохранение отчета о транзакциях."""
    if report.user_id not in transaction_reports:
        transaction_reports[report.user_id] = []

    transaction_reports[report.user_id].append(
        TransactionReport(
            report.date_start,
            report.date_end,
            user_transactions,
        ),
    )


def get_transactions_view(
    report: TransactionReportSchema,
) -> list[Transaction]:
    """Получение списка транзакций."""
    user_transactions = []
    for transaction in transactions[report.user_id]:
        if report.date_start < transaction.date < report.date_end:
            user_transactions.append(transaction)

    save_report(report, user_transactions)

    return user_transactions
