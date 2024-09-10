import asyncio
from datetime import datetime
from typing import AsyncGenerator
from unittest.mock import Mock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_helper import DatabaseHelper
from app.db.db_helper import db_helper as db_session_helper
from app.db.models import BaseTable, TransactionType, User, UserTransaction
from app.main import app
from app.transaction_service.schemas import TransactionOutSchema

TEST_DB_URL = 'postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/test_db'  # noqa: E501
test_db_helper = DatabaseHelper(url=TEST_DB_URL, echo=True)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_db_helper.session_factory() as session:
        yield session

app.dependency_overrides[db_session_helper.scoped_session_dependency] = (
    override_get_async_session
)


@pytest_asyncio.fixture()
async def reset_db():
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.create_all)
    yield
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def db_helper() -> DatabaseHelper:
    return test_db_helper


@pytest_asyncio.fixture()
async def user() -> User:
    async with test_db_helper.session_factory() as session:
        user = User(name='user11', password=b'password')
        session.add(user)
        await session.commit()
        return user


@pytest_asyncio.fixture()
async def withdrawal_id() -> int:
    async with test_db_helper.session_factory() as session:
        transaction_type = TransactionType(name='Снятие')
        session.add(transaction_type)
        await session.commit()
        return transaction_type.id


@pytest_asyncio.fixture()
async def deposit_id() -> int:
    async with test_db_helper.session_factory() as session:
        transaction_type = TransactionType(name='Пополнение')
        session.add(transaction_type)
        await session.commit()
        return transaction_type.id


@pytest_asyncio.fixture()
async def user_and_transactions(
    user: User,
    withdrawal_id: int,
    deposit_id: int,
) -> tuple[User, list[TransactionOutSchema]]:
    async with test_db_helper.session_factory() as session:
        transaction_1 = UserTransaction(
            user_id=user.id,
            amount=100,
            transaction_type_id=withdrawal_id,
            date=datetime.now(),
        )
        transaction_2 = UserTransaction(
            user_id=user.id,
            amount=300,
            transaction_type_id=deposit_id,
            date=datetime.now(),
        )

        session.add_all([transaction_1, transaction_2])
        await session.commit()

        tranactions = [
            TransactionOutSchema.model_validate(transaction_1),
            TransactionOutSchema.model_validate(transaction_2),
        ]
        return user, tranactions


def get_redis_mock() -> Mock:
    redis_cashe: dict[str, int | str] = {}

    def get_type_id(type_name: str):
        return redis_cashe.get(f'tt_id:{type_name}', None)

    def set_type_id(type_name: str, type_id: int):
        redis_cashe[f'tt_id:{type_name}'] = type_id

    def get_transaction(report_key: str):
        return redis_cashe.get(report_key, None)

    def set_report_transaction(report_key: str, value: str):
        redis_cashe[f'report:{report_key}'] = value

    redis_client = Mock()
    redis_client.get_transaciton_type_id = get_type_id
    redis_client.set_transaciton_type_id = set_type_id
    redis_client.get_report_transaction = get_transaction
    redis_client.set_report_transaction = set_report_transaction

    redis_client.get_cash = lambda: redis_cashe

    return redis_client


@pytest.fixture
def redis_mock() -> Mock:
    return get_redis_mock()
