"""create Strategy table

Revision ID: a4f165a6b7cb
Revises: 
Create Date: 2024-01-09 02:13:50.345746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'a4f165a6b7cb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('strategy',
    sa.Column('strategy_id', sa.String(length=50), nullable=True),
    sa.Column('position_size', sa.Float(), nullable=True),
    sa.Column('parameter_1', sa.String(length=50), nullable=True),
    sa.Column('value_1', sa.String(length=50), nullable=True),
    sa.Column('parameter_2', sa.String(length=50), nullable=True),
    sa.Column('value_2', sa.String(length=50), nullable=True),
    sa.Column('parameter_3', sa.String(length=50), nullable=True),
    sa.Column('value_3', sa.String(length=50), nullable=True),
    sa.Column('parameter_4', sa.String(length=50), nullable=True),
    sa.Column('value_4', sa.String(length=50), nullable=True),
    sa.Column('id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('strategy')
    # ### end Alembic commands ###
