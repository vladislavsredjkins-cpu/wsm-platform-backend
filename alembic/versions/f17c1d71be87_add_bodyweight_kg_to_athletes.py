"""add bodyweight_kg to athletes

Revision ID: f17c1d71be87
Revises: 61ba6e7c7c79
Create Date: 2026-03-09 17:26:49.411563
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f17c1d71be87'
down_revision: Union[str, None] = '61ba6e7c7c79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('athletes', sa.Column('bodyweight_kg', sa.Numeric(precision=5, scale=2), nullable=True))

def downgrade() -> None:
    op.drop_column('athletes', 'bodyweight_kg')
