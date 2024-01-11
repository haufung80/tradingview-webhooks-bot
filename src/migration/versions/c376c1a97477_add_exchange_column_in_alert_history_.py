"""add exchange column in alert_history table

Revision ID: c376c1a97477
Revises: 0d8f1ad0f654
Create Date: 2024-01-09 16:43:53.464428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c376c1a97477'
down_revision: Union[str, None] = '0d8f1ad0f654'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alert_history', sa.Column('exchange', sa.String(length=50), nullable=True))
    op.drop_column('alert_history', 'symbol')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alert_history', sa.Column('symbol', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_column('alert_history', 'exchange')
    # ### end Alembic commands ###