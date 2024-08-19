from datetime import datetime

import pytest
import sqlalchemy

from app.db.models import TransactionReport, TransactionType, UserTransaction


@pytest.mark.parametrize(
    'name',
    [
        pytest.param('Пополнение', id='deposit'),
        pytest.param('Снятие', id='withdrawal'),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_transaction_type_model(name, db_helper):
    transaction_type = TransactionType(name=name)

    async with db_helper.session_factory() as session:
        session.add(transaction_type)
        await session.commit()


@pytest.mark.parametrize(
    'amount',
    [
        pytest.param(0, id='deposit zero'),
        pytest.param(1000, id='deposit'),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_transaction_model(amount, user, deposit_id, db_helper):
    transaction_in = UserTransaction(
        user_id=user.id,
        amount=amount,
        transaction_type_id=deposit_id,
        date=datetime.now(),
    )

    async with db_helper.session_factory() as session:
        session.add(transaction_in)
        await session.commit()

    async with db_helper.session_factory() as session:
        transaction_out = await session.get(UserTransaction, transaction_in.id)

    assert transaction_out.amount == amount
    assert transaction_out.transaction_type_id == deposit_id
    assert transaction_out.date


@pytest.mark.parametrize(
    'amount, date, error_msg',
    [
        pytest.param(
            None,
            datetime.now(),
            'значение NULL в столбце "amount"',
            id='no_amount',
        ),
        pytest.param(
            100,
            None,
            'значение NULL в столбце "date"',
            id='no_date',
        ),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_transaction_model_field_null(
    amount, date, error_msg, user, deposit_id, db_helper,
):
    transaction = UserTransaction(
        user_id=user.id,
        amount=amount,
        transaction_type_id=deposit_id,
        date=date,
    )
    async with db_helper.session_factory() as session:
        with pytest.raises(sqlalchemy.exc.IntegrityError) as ex:
            session.add(transaction)
            await session.commit()

    assert error_msg in str(ex.value)


@pytest.mark.parametrize(
    'user_id_wrong, transaction_type_id_wrong, error_msg',
    [
        pytest.param(
            0,
            1,
            'Ключ (transaction_type_id)=(1000) отсутствует в таблице',
            id='bad_transaction_type',
        ),
        pytest.param(
            1,
            0,
            'Ключ (user_id)=(1000) отсутствует в таблице',
            id='bad_user_id',
        ),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_transaction_model_no_foreign(
    user_id_wrong,
    transaction_type_id_wrong,
    error_msg,
    user,
    deposit_id,
    db_helper,
):
    if user_id_wrong:
        user.id = 1000
    if transaction_type_id_wrong:
        deposit_id = 1000

    transaction = UserTransaction(
        user_id=user.id,
        amount=100,
        transaction_type_id=deposit_id,
        date=datetime.now(),
    )
    async with db_helper.session_factory() as session:
        with pytest.raises(sqlalchemy.exc.IntegrityError) as ex:
            session.add(transaction)
            await session.commit()

    assert error_msg in str(ex.value)


@pytest.mark.parametrize(
    'date_start, date_end',
    [
        pytest.param(
            datetime(2024, 1, 1),
            datetime(2124, 1, 1),
            id='long_period',
        ),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_transaction_report_model(date_start, date_end, user, db_helper):
    report = TransactionReport(
        user_id=user.id,
        date_start=date_start,
        date_end=date_end,
    )

    async with db_helper.session_factory() as session:
        session.add(report)
        await session.commit()

    async with db_helper.session_factory() as session:
        report_out = await session.get(TransactionReport, report.id)

    assert report_out.user_id == user.id
    assert report_out.date_start == date_start
    assert report_out.date_end == date_end


@pytest.mark.parametrize(
    'date_start, date_end, error_msg',
    [
        pytest.param(
            datetime(2024, 1, 1),
            None,
            'значение NULL в столбце "date_end"',
            id='no_date_end',
        ),
        pytest.param(
            None,
            datetime(2124, 1, 1),
            'значение NULL в столбце "date_start"',
            id='no_date_start',
        ),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_transaction_report_field_null(
    date_start, date_end, error_msg, user, db_helper,
):
    report = TransactionReport(
        user_id=user.id,
        date_start=date_start,
        date_end=date_end,
    )
    async with db_helper.session_factory() as session:
        with pytest.raises(sqlalchemy.exc.IntegrityError) as ex:
            session.add(report)
            await session.commit()

    assert error_msg in str(ex.value)


@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_transaction_report_no_foreign(db_helper):
    report = TransactionReport(
        user_id=1000,
        date_start=datetime(2024, 1, 1),
        date_end=datetime(2124, 1, 1),
    )
    async with db_helper.session_factory() as session:
        with pytest.raises(sqlalchemy.exc.IntegrityError) as ex:
            session.add(report)
            await session.commit()

    assert 'Ключ (user_id)=(1000) отсутствует в таблице' in str(ex.value)
