import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.transaction_service.views import transaction_reports, transactions


@pytest.fixture(autouse=True)
def setup():
    transactions.clear()
    transaction_reports.clear()


@pytest_asyncio.fixture(scope='session')
async def ac():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
