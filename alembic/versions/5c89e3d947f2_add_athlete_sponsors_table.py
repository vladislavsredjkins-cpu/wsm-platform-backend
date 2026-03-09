"""add athlete_sponsors table

Revision ID: 5c89e3d947f2
Revises: f17c1d71be87
Create Date: 2026-03-09 17:35:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '5c89e3d947f2'
down_revision: Union[str, None] = 'f17c1d71be87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('athlete_sponsors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('tier', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('athlete_sponsors')
