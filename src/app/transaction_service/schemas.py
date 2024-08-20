from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class TransactionTypeSchema(Enum):
    """Тип транзакции."""

    DEPOSIT = 'Пополнение'
    WITHDRAWAL = 'Снятие'


class TransactionSchema(BaseModel):
    """Схема транзакции."""

    user_id: int
    amount: int
    transaction_type: TransactionTypeSchema


class TransactionOutSchema(BaseModel):
    """Схема вывода транзакции."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    amount: int
    transaction_type_id: int
    date: datetime


class TransactionReportSchema(BaseModel):
    """Схема отчета о транзакциях."""

    user_id: int
    date_start: datetime
    date_end: datetime
