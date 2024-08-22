from datetime import datetime

from sqlalchemy import ForeignKey, MetaData, String
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
)
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Numeric

from app.config import settings

schema = settings.db_schema

Base = declarative_base(
    metadata=MetaData(schema=schema),
)


class BaseTable(Base):  # type: ignore
    """Базовая модель."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class User(BaseTable):
    """Модель пользователя."""

    __tablename__ = 'lebedev_user'

    name: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[bytes]
    balance: Mapped[int] = mapped_column(BigInteger, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_vector: Mapped[list[float] | None] = mapped_column(
        ARRAY(Numeric(8, 7)),
    )


class TransactionType(BaseTable):
    """Модель типа транзакции."""

    __tablename__ = 'lebedev_transaction_type'

    name: Mapped[str] = mapped_column(String(100), unique=True)


class UserTransaction(BaseTable):
    """Модель транзакции пользователя."""

    __tablename__ = 'lebedev_user_transaction'

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f'{schema}.lebedev_user.id'),
    )
    amount: Mapped[int] = mapped_column(BigInteger)
    transaction_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f'{schema}.{TransactionType.__tablename__}.id'),
    )
    date: Mapped[datetime]


class TransactionReport(BaseTable):
    """Модель отчета о транзакциях."""

    __tablename__ = 'lebedev_transaction_report'

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f'{schema}.lebedev_user.id'),
    )
    date_start: Mapped[datetime]
    date_end: Mapped[datetime]

    transactions: Mapped[list[UserTransaction]] = relationship(
        secondary=f'{schema}.lebedev_transaction_report_relation',
    )


class ReportTransactionRelation(BaseTable):
    """Модель связи отчета и транзакции."""

    __tablename__ = 'lebedev_transaction_report_relation'

    report_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f'{schema}.{TransactionReport.__tablename__}.id'),
    )
    transaction_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f'{schema}.{UserTransaction.__tablename__}.id'),
    )
