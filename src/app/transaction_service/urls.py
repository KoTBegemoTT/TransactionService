from fastapi import APIRouter, status

from app.models import Transaction
from app.transaction_service.schemas import (
    TransactionReportSchema,
    TransactionSchema,
)
from app.transaction_service.views import (
    create_transaction_view,
    get_transactions_view,
)

router = APIRouter(tags=['transactions'])


@router.post(
    '/create/',
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(transaction: TransactionSchema) -> None:
    """Создание новой транзакции."""
    return await create_transaction_view(transaction)


@router.post(
    '/report/',
    status_code=status.HTTP_201_CREATED,
)
async def get_transactions(
    transaction_report: TransactionReportSchema,
) -> list[Transaction]:
    """Получение списка транзакции."""
    return await get_transactions_view(transaction_report)
