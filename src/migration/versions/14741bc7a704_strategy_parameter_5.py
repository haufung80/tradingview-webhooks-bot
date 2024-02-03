"""strategy parameter 5

Revision ID: 14741bc7a704
Revises: 419b724e86e4
Create Date: 2024-02-02 22:30:09.763157

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '14741bc7a704'
down_revision: Union[str, None] = '419b724e86e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strategy', sa.Column('parameter_5', sa.String(length=50), nullable=True))
    op.add_column('strategy', sa.Column('value_5', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('strategy', 'value_5')
    op.drop_column('strategy', 'parameter_5')
    # ### end Alembic commands ###