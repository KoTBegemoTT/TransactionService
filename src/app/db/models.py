from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Numeric


class Base(DeclarativeBase):
    """Базовая модель."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'lebedev_user'

    name: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[bytes]
    balance: Mapped[int] = mapped_column(BigInteger, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_vector: Mapped[list[float] | None] = mapped_column(
        ARRAY(Numeric(8, 7)),
    )


class TransactionType(Base):
    """Модель типа транзакции."""

    __tablename__ = 'lebedev_transaction_type'

    name: Mapped[str] = mapped_column(String(100), unique=True)


class UserTransaction(Base):
    """Модель транзакции пользователя."""

    __tablename__ = 'lebedev_user_transaction'

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('lebedev_user.id'),
    )
    amount: Mapped[int] = mapped_column(BigInteger)
    transaction_type_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('lebedev_transaction_type.id'),
    )
    date: Mapped[datetime]


class TransactionReport(Base):
    """Модель отчета о транзакциях."""

    __tablename__ = 'lebedev_transaction_report'

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('lebedev_user.id'),
    )
    date_start: Mapped[datetime]
    date_end: Mapped[datetime]

    transactions: Mapped[list[UserTransaction]] = relationship(
        secondary='lebedev_transaction_report_relation',
    )


class ReportTransactionRelation(Base):
    """Модель связи отчета и транзакции."""

    __tablename__ = 'lebedev_transaction_report_relation'

    report_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('lebedev_transaction_report.id'),
    )
    transaction_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('lebedev_user_transaction.id'),
    )
