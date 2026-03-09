"""add judges tables

Revision ID: d97b79df2e37
Revises: 662bdaf96ae3
Create Date: 2026-03-09 18:10:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd97b79df2e37'
down_revision: Union[str, None] = '662bdaf96ae3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('judges',
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
        sa.Column('level', sa.String(length=50), nullable=True),
        sa.Column('instagram', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_table('judge_certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('judge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('issued_by', sa.String(length=300), nullable=True),
        sa.Column('issued_date', sa.Date(), nullable=True),
        sa.Column('expires_date', sa.Date(), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['judge_id'], ['judges.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('judge_competitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('judge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['judge_id'], ['judges.id']),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('judge_competitions')
    op.drop_table('judge_certificates')
    op.drop_table('judges')
