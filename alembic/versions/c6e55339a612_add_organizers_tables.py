"""add organizers tables

Revision ID: c6e55339a612
Revises: d97b79df2e37
Create Date: 2026-03-09 18:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6e55339a612'
down_revision: Union[str, None] = 'd97b79df2e37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('organizers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('country', sa.String(length=10), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('instagram', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_table('organizer_sponsors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('tier', sa.String(length=20), nullable=False),
        sa.Column('paid_until', sa.Date(), nullable=True),
        sa.Column('price_paid', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['organizer_id'], ['organizers.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('organizer_sponsors')
    op.drop_table('organizers')
