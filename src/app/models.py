from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """Класс транзакции."""

    amount: float
    transaction_type: str
    date: datetime = datetime.now()


@dataclass
class TransactionReport:
    """Класс отчета о транзакциях."""

    user_id: int
    date_start: datetime
    date_end: datetime
    transactions: list[Transaction]
