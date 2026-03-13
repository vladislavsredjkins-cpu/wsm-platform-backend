"""add result_type unit to match_discipline_results
Revision ID: ddf0c5ea7915
Revises: 97f7bc2fbd54
Create Date: 2026-03-12
"""
from alembic import op
import sqlalchemy as sa

revision = 'ddf0c5ea7915'
down_revision = '97f7bc2fbd54'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('match_discipline_results', sa.Column('result_type', sa.String(20), nullable=True, server_default='higher_wins'))
    op.add_column('match_discipline_results', sa.Column('unit', sa.String(10), nullable=True))

def downgrade() -> None:
    op.drop_column('match_discipline_results', 'unit')
    op.drop_column('match_discipline_results', 'result_type')
