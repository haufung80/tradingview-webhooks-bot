"""add strategy expiry_date

Revision ID: bbb49a462680
Revises: 3496f590d681
Create Date: 2024-01-11 14:06:04.760118

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'bbb49a462680'
down_revision: Union[str, None] = '3496f590d681'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strategy', sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('strategy', 'expiry_date')
    # ### end Alembic commands ###
