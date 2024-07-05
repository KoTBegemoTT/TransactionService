from datetime import datetime

from app.models import Transaction, TransactionReport, TransactionType

transactions: dict[int, list[Transaction]] = {}
transaction_reports: list[TransactionReport] = []


class TransactionService:
    """Сервис для сохранения и обработки пользовательских транзакций."""

    @staticmethod
    def create_transaction(
        user_id: int,
        amount: float | int,
        transaction_type: TransactionType | str,
    ) -> None:
        """Создание новой транзакции."""
        if not isinstance(user_id, int):
            raise TypeError('user_id must be int')

        if isinstance(transaction_type, str):
            transaction_type = TransactionType(transaction_type)

        transaction = Transaction(amount, transaction_type, datetime.now())
        if user_id not in transactions:
            transactions[user_id] = [transaction]
        else:
            transactions[user_id].append(transaction)

    @staticmethod
    def save_report(
        user_id: int,
        date_start: datetime,
        date_end: datetime,
        user_transactions: list[Transaction],
    ) -> None:
        """Сохранение отчета о транзакциях."""
        transaction_reports.append(
            TransactionReport(
                user_id,
                date_start,
                date_end,
                user_transactions,
            )
        )

    @staticmethod
    def get_transactions(
        user_id,
        date_start: datetime,
        date_end: datetime,
    ) -> list[Transaction]:
        """Получение списка транзакций."""
        if not isinstance(date_start, datetime) or not isinstance(date_end, datetime):  # noqa: E501
            raise TypeError('date_start and date_end must be datetime')

        user_transactions = []
        for transaction in transactions[user_id]:
            if date_start < transaction.date < date_end:
                user_transactions.append(transaction)

        TransactionService.save_report(
            user_id,
            date_start,
            date_end,
            user_transactions,
        )

        return user_transactions
