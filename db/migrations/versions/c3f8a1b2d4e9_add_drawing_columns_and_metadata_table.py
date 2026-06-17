"""Add winner/day_of_week/winner_state to drawings and create drawing_metadata table

Revision ID: c3f8a1b2d4e9
Revises: a8d75e978d9f
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3f8a1b2d4e9'
down_revision: Union[str, None] = 'a8d75e978d9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('drawings', sa.Column('winner', sa.Boolean(), nullable=True))
    op.add_column('drawings', sa.Column('day_of_week', sa.Integer(), nullable=True))
    op.add_column('drawings', sa.Column('winner_state', sa.String(), nullable=True))

    op.create_table(
        'drawing_metadata',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('drawing_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['drawing_id'], ['drawings.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('drawing_metadata')
    op.drop_column('drawings', 'winner_state')
    op.drop_column('drawings', 'day_of_week')
    op.drop_column('drawings', 'winner')
