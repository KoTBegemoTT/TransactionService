from datetime import datetime

from app.models import Transaction, TransactionReport
from app.transaction_service.schemas import (
    TransactionReportSchema,
    TransactionSchema,
)

transactions: dict[int, list[Transaction]] = {}
transaction_reports: dict[int, dict[str, TransactionReport]] = {}


async def create_transaction_view(transaction: TransactionSchema) -> None:
    """Создание новой транзакции."""
    transaction_bd = Transaction(
        transaction.amount,
        transaction.transaction_type,
        datetime.now(),
    )
    if transaction.user_id not in transactions:
        transactions[transaction.user_id] = [transaction_bd]
    else:
        transactions[transaction.user_id].append(transaction_bd)


def concat_date(date_start: datetime, date_end: datetime) -> str:
    """Соединяет даты в строку."""
    return f'{date_start.isoformat()} - {date_end.isoformat()}'


async def save_report(
    report: TransactionReportSchema,
    user_transactions: list[Transaction],
) -> None:
    """Сохранение отчета о транзакциях."""
    if report.user_id not in transaction_reports:
        transaction_reports[report.user_id] = {}

    report_dates = concat_date(report.date_start, report.date_end)
    transaction_reports[report.user_id][report_dates] = TransactionReport(
        report.date_start,
        report.date_end,
        user_transactions,
    )


async def found_report(
    report: TransactionReportSchema,
) -> TransactionReport | None:
    """Поиск отчета о транзакциях."""
    if report.user_id not in transaction_reports:
        return None

    user_reports = transaction_reports[report.user_id]
    report_dates = concat_date(report.date_start, report.date_end)
    return user_reports.get(report_dates, None)


async def get_transactions_view(
    report: TransactionReportSchema,
) -> list[Transaction]:
    """Получение списка транзакций."""
    existing_report = await found_report(report)
    if existing_report:
        return existing_report.transactions

    user_transactions = []
    for transaction in transactions[report.user_id]:
        if report.date_start < transaction.date < report.date_end:
            user_transactions.append(transaction)

    await save_report(report, user_transactions)

    return user_transactions
