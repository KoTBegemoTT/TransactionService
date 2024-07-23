from datetime import datetime

import pytest

from app.models import Transaction, TransactionReport, TransactionType


@pytest.mark.parametrize(
    'transaction_type_in',
    [
        pytest.param('Пополнение', id='deposit'),
        pytest.param('Снятие', id='withdrawal'),
    ],
)
def test_transaction_type_model(transaction_type_in):
    transaction_type = TransactionType(transaction_type_in)

    assert transaction_type.value == transaction_type_in


@pytest.mark.parametrize(
    'transaction_type, error_msg',
    [
        pytest.param(
            'WRONG_TYPE',
            "'WRONG_TYPE' is not a valid TransactionType",
            id='wrong_string'),
        pytest.param(
            None,
            'None is not a valid TransactionType',
            id='None_type'),
    ],
)
def test_transaction_type_model_fail(transaction_type, error_msg):
    with pytest.raises(ValueError) as ex:
        TransactionType(transaction_type)

    assert ex.value.args[0] == error_msg


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {
                'amount': 100,
                'transaction_type': TransactionType.DEPOSIT,
            },
            id='deposit',
        ),
        pytest.param(
            {
                'amount': 1000,
                'transaction_type': TransactionType.WITHDRAWAL,
            },
            id='withdrawal',
        ),
    ],
)
def test_transaction_model(pyload):
    transaction = Transaction(**pyload)

    assert transaction.amount == pyload['amount']
    assert transaction.transaction_type == pyload['transaction_type']
    assert transaction.date


@pytest.mark.parametrize(
    'pyload, error_msg',
    [
        pytest.param(
            {
                'transaction_type': TransactionType.DEPOSIT,
            },
            "Transaction.__init__() missing 1 required positional argument: 'amount'",  # noqa: E501
            id='no_amount',
        ),
        pytest.param(
            {
                'amount': 100,
            },
            "Transaction.__init__() missing 1 required positional argument: 'transaction_type'",  # noqa: E501
            id='no_transaction_type',
        ),
    ],
)
def test_transaction_model_fail(pyload, error_msg):
    with pytest.raises(TypeError) as ex:
        Transaction(**pyload)

    assert ex.value.args[0] == error_msg


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {
                'date_start': datetime(2024, 1, 1),
                'date_end': datetime(2124, 1, 1),
                'transactions': [],
            },
            id='deposit',
        ),
    ],
)
def test_transaction_report_model(pyload):
    report = TransactionReport(**pyload)

    assert report.date_start == pyload['date_start']
    assert report.date_end == pyload['date_end']
    assert report.transactions == pyload['transactions']


@pytest.mark.parametrize(
    'pyload, error_msg',
    [
        pytest.param(
            {
                'date_end': datetime(2124, 1, 1),
                'transactions': [],
            },
            "TransactionReport.__init__() missing 1 required positional argument: 'date_start'",  # noqa: E501
            id='no_date_start',
        ),
        pytest.param(
            {
                'date_start': datetime(2024, 1, 1),
                'transactions': [],
            },
            "TransactionReport.__init__() missing 1 required positional argument: 'date_end'",  # noqa: E501
            id='no_date_end',
        ),
        pytest.param(
            {
                'date_start': datetime(2024, 1, 1),
                'date_end': datetime(2124, 1, 1),
            },
            "TransactionReport.__init__() missing 1 required positional argument: 'transactions'",  # noqa: E501
            id='no_transactions',
        ),
    ],
)
def test_transaction_report_fail_model(pyload, error_msg):
    with pytest.raises(TypeError) as ex:
        TransactionReport(**pyload)

    assert ex.value.args[0] == error_msg
