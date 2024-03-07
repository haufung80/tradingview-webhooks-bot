"""backtest result for strategy

Revision ID: 46a3a2cf3fe2
Revises: 8a276cb31812
Create Date: 2024-03-07 15:12:22.780205

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '46a3a2cf3fe2'
down_revision: Union[str, None] = '8a276cb31812'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strategy', sa.Column('backtest_period', sa.String(length=10), nullable=True))
    op.add_column('strategy', sa.Column('wfe', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('sr', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('l_sr', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('b_sr', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('win_rate', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('trd_num', mysql.INTEGER(), nullable=True))
    op.add_column('strategy', sa.Column('sim_ret', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('lev_ret', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('bnh_ret', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('sim_mdd', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('lev_mdd', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('bnh_mdd', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('lev_add', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('bnh_add', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('expos', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('leverage', sa.Float(), nullable=True))
    op.add_column('strategy', sa.Column('timeframe', sa.String(length=20), nullable=True))
    op.drop_column('strategy', 'expiry_date')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strategy',
                  sa.Column('expiry_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.drop_column('strategy', 'timeframe')
    op.drop_column('strategy', 'leverage')
    op.drop_column('strategy', 'expos')
    op.drop_column('strategy', 'bnh_add')
    op.drop_column('strategy', 'lev_add')
    op.drop_column('strategy', 'bnh_mdd')
    op.drop_column('strategy', 'lev_mdd')
    op.drop_column('strategy', 'sim_mdd')
    op.drop_column('strategy', 'bnh_ret')
    op.drop_column('strategy', 'lev_ret')
    op.drop_column('strategy', 'sim_ret')
    op.drop_column('strategy', 'trd_num')
    op.drop_column('strategy', 'win_rate')
    op.drop_column('strategy', 'b_sr')
    op.drop_column('strategy', 'l_sr')
    op.drop_column('strategy', 'sr')
    op.drop_column('strategy', 'wfe')
    op.drop_column('strategy', 'backtest_period')
    # ### end Alembic commands ###