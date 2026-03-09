"""add coaches tables

Revision ID: 82c76ad97bc6
Revises: ca1d65ccae32
Create Date: 2026-03-09 19:10:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '82c76ad97bc6'
down_revision: Union[str, None] = 'ca1d65ccae32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('coaches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=10), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('instagram', sa.String(length=100), nullable=True),
        sa.Column('level', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_table('coach_certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('coach_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('issued_by', sa.String(length=300), nullable=True),
        sa.Column('issued_date', sa.Date(), nullable=True),
        sa.Column('expires_date', sa.Date(), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['coach_id'], ['coaches.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('coach_certificates')
    op.drop_table('coaches')
