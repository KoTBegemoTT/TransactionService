from datetime import datetime

from pydantic import BaseModel

from app.models import TransactionType


class TransactionSchema(BaseModel):
    """Схема транзакции."""

    user_id: int
    amount: float
    transaction_type: TransactionType


class TransactionReportSchema(BaseModel):
    """Схема отчета о транзакциях."""

    user_id: int
    date_start: datetime
    date_end: datetime
