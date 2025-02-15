"""create tables with schema

Revision ID: 2c4f2c146d27
Revises: 
Create Date: 2024-08-22 05:47:07.918155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c4f2c146d27'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lebedev_transaction_type',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='lebedev_schema'
    )
    op.create_table('lebedev_user',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('password', sa.LargeBinary(), nullable=False),
    sa.Column('balance', sa.BigInteger(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('verification_vector', sa.ARRAY(sa.Numeric(precision=8, scale=7)), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='lebedev_schema'
    )
    op.create_table('lebedev_transaction_report',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('date_start', sa.DateTime(), nullable=False),
    sa.Column('date_end', sa.DateTime(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['lebedev_schema.lebedev_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='lebedev_schema'
    )
    op.create_table('lebedev_user_transaction',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=False),
    sa.Column('transaction_type_id', sa.BigInteger(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['transaction_type_id'], ['lebedev_schema.lebedev_transaction_type.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['lebedev_schema.lebedev_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='lebedev_schema'
    )
    op.create_table('lebedev_transaction_report_relation',
    sa.Column('report_id', sa.BigInteger(), nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['report_id'], ['lebedev_schema.lebedev_transaction_report.id'], ),
    sa.ForeignKeyConstraint(['transaction_id'], ['lebedev_schema.lebedev_user_transaction.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='lebedev_schema'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lebedev_transaction_report_relation', schema='lebedev_schema')
    op.drop_table('lebedev_user_transaction', schema='lebedev_schema')
    op.drop_table('lebedev_transaction_report', schema='lebedev_schema')
    op.drop_table('lebedev_user', schema='lebedev_schema')
    op.drop_table('lebedev_transaction_type', schema='lebedev_schema')
    # ### end Alembic commands ###
