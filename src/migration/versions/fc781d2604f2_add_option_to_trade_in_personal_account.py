"""add option to trade in personal account

Revision ID: fc781d2604f2
Revises: 80dd0105b847
Create Date: 2024-01-30 14:56:48.351399

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fc781d2604f2'
down_revision: Union[str, None] = '80dd0105b847'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strategy', sa.Column('personal_acc', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('strategy', 'personal_acc')
    # ### end Alembic commands ###