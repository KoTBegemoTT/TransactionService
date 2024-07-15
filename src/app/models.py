from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """Тип транзакции."""

    DEPOSIT = 'Пополнение'
    WITHDRAWAL = 'Снятие'


@dataclass
class Transaction:
    """Класс транзакции."""

    amount: float
    transaction_type: TransactionType
    date: datetime = datetime.now()


@dataclass
class TransactionReport:
    """Класс отчета о транзакциях."""

    date_start: datetime
    date_end: datetime
    transactions: list[Transaction]
