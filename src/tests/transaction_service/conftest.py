from datetime import datetime
import pytest
from app.logic import transactions, transaction_reports
from app.models import Transaction, TransactionType


@pytest.fixture(autouse=True)
def setup():
    transactions.clear()
    transaction_reports.clear()


@pytest.fixture
def add_user_1_transactions():
    transactions[1] = []
    transactions[1].append(Transaction(100, TransactionType.DEPOSIT, datetime.now()))
    transactions[1].append(Transaction(300, TransactionType.WITHDRAWAL, datetime.now()))
    transactions[1].append(Transaction(1000, TransactionType.DEPOSIT, datetime.now()))
