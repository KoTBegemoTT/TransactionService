from datetime import datetime

import pytest
from pydantic_core import ValidationError

from app.models import TransactionType
from app.transaction_service.schemas import (
    TransactionReportSchema,
    TransactionSchema,
)


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {
                'user_id': 1,
                'amount': 100,
                'transaction_type': TransactionType.DEPOSIT,
            },
            id='user_1',
        ),
        pytest.param(
            {
                'user_id': 2,
                'amount': 100.73,
                'transaction_type': TransactionType.DEPOSIT,
            },
            id='float_amount',
        ),
        pytest.param(
            {
                'user_id': 1000,
                'amount': 1000,
                'transaction_type': TransactionType.WITHDRAWAL,
            },
            id='withdrawl_user_1000',
        ),
    ],
)
def test_transaction_schema(pyload):
    transaciton = TransactionSchema(**pyload)
    assert transaciton.user_id == pyload.get('user_id')
    assert transaciton.amount == pyload.get('amount')
    assert transaciton.transaction_type == pyload.get('transaction_type')


@pytest.mark.parametrize(
    'pyload, bad_field, error_msg',
    [
        pytest.param
        (
            {
                'amount': 100,
                'transaction_type': TransactionType.DEPOSIT,
            },
            'user_id',
            'Field required',
            id='no_user_id',
        ),
        pytest.param
        (
            {
                'user_id': 1,
                'transaction_type': TransactionType.DEPOSIT,
            },
            'amount',
            'Field required',
            id='no_amount',
        ),
        pytest.param
        (
            {
                'user_id': 1000,
                'amount': 1000,
            },
            'transaction_type',
            'Field required',
            id='no_transaction_type',
        ),
        pytest.param
        (
            {
                'user_id': None,
                'amount': 100,
                'transaction_type': TransactionType.DEPOSIT,
            },
            'user_id',
            'Input should be a valid integer',
            id='user_id_none',
        ),
        pytest.param
        (
            {
                'user_id': 1,
                'amount': None,
                'transaction_type': TransactionType.DEPOSIT,
            },
            'amount',
            'Input should be a valid number',
            id='amount_none',
        ),
        pytest.param
        (
            {
                'user_id': 1,
                'amount': 100,
                'transaction_type': 'Wrong_type',
            },
            'transaction_type',
            "Input should be 'Пополнение' or 'Снятие'",
            id='transaction_type_bad_type',
        ),
    ],
)
def test_transaction_schema_fail(pyload, bad_field, error_msg):
    with pytest.raises(ValidationError) as ex:
        TransactionSchema(**pyload)

    assert ex.value.error_count() == 1
    ex_info = ex.value.errors()[0]
    assert ex_info['loc'] == (bad_field,)
    assert ex_info['msg'] == error_msg


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {
                'user_id': 1,
                'date_start': datetime(2024, 1, 1),
                'date_end': datetime(2124, 1, 1),
            },
            id='user_1',
        ),
    ],
)
def test_transaction_report_schema(pyload):
    transaciton = TransactionReportSchema(**pyload)
    assert transaciton.user_id == pyload.get('user_id')
    assert transaciton.date_start == pyload.get('date_start')
    assert transaciton.date_end == pyload.get('date_end')


@pytest.mark.parametrize(
    'pyload, bad_field, error_msg',
    [
        pytest.param
        (
            {
                'date_start': datetime(2024, 1, 1),
                'date_end': datetime(2124, 1, 1),
            },
            'user_id',
            'Field required',
            id='no_user_id',
        ),
        pytest.param
        (
            {
                'user_id': 1,
                'date_end': datetime(2124, 1, 1),
            },
            'date_start',
            'Field required',
            id='no_date_start',
        ),
        pytest.param
        (
            {
                'user_id': 1,
                'date_start': datetime(2124, 1, 1),
            },
            'date_end',
            'Field required',
            id='no_date_end',
        ),
        pytest.param
        (
            {
                'user_id': None,
                'date_start': datetime(2024, 1, 1),
                'date_end': datetime(2124, 1, 1),
            },
            'user_id',
            'Input should be a valid integer',
            id='user_id_none',
        ),
        pytest.param
        (
            {
                'user_id': 1,
                'date_start': None,
                'date_end': datetime(2124, 1, 1),
            },
            'date_start',
            'Input should be a valid datetime',
            id='date_start_none',
        ),
        pytest.param
        (
            {
                'user_id': 1,
                'date_start': datetime(2024, 1, 1),
                'date_end': None,
            },
            'date_end',
            'Input should be a valid datetime',
            id='date_end_none',
        ),
    ],
)
def test_transaction_report_schema_fail(pyload, bad_field, error_msg):
    with pytest.raises(ValidationError) as ex:
        TransactionReportSchema(**pyload)

    assert ex.value.error_count() == 1
    ex_info = ex.value.errors()[0]
    assert ex_info['loc'] == (bad_field,)
    assert ex_info['msg'] == error_msg
