from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class TransactionType(Enum):
    """Тип транзакции."""

    DEPOSIT = 'Пополнение'
    WITHDRAWAL = 'Снятие'


class TransactionSchema(BaseModel):
    """Схема транзакции."""

    user_id: int
    amount: int
    transaction_type: TransactionType


class TransactionOutSchema(BaseModel):
    """Схема вывода транзакции."""

    user_id: int
    amount: float
    transaction_type: TransactionType
    date: datetime



class TransactionReportSchema(BaseModel):
    """Схема отчета о транзакциях."""

    user_id: int
    date_start: datetime
    date_end: datetime
