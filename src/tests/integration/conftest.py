import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.transaction_service.views import transaction_reports, transactions

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():
    transactions.clear()
    transaction_reports.clear()


@pytest.fixture(scope='session')
def test_client():
    return client
