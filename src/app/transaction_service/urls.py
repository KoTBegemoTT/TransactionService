from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_helper import db_helper
from app.transaction_service.schemas import (
    TransactionOutSchema,
    TransactionReportSchema,
    TransactionSchema,
)
from app.transaction_service.views import (
    create_transaction_view,
    get_transactions_view,
)

router = APIRouter(tags=['transactions'])


@router.get(
    '/healthz/ready/',
    status_code=status.HTTP_200_OK,
)
async def ready_check() -> None:
    """Проверка состояния сервиса."""
    return None


@router.post(
    '/transactions/create/',
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transaction: TransactionSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    """Создание новой транзакции."""
    return await create_transaction_view(transaction, session)


@router.post(
    '/transactions/report/',
    status_code=status.HTTP_201_CREATED,
)
async def get_transactions(
    transaction_report: TransactionReportSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> list[TransactionOutSchema]:
    """Получение списка транзакции."""
    return await get_transactions_view(transaction_report, session)
