"""catch error for each exhcange

Revision ID: 75ec4e1703ec
Revises: 9fe3c0423593
Create Date: 2024-02-17 16:42:05.020874

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '75ec4e1703ec'
down_revision: Union[str, None] = '9fe3c0423593'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_execution_error', sa.Column('exchange', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_execution_error', 'exchange')
    # ### end Alembic commands ###
