"""add teams tables

Revision ID: 9be4784da290
Revises: 82c76ad97bc6
Create Date: 2026-03-09 19:20:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '9be4784da290'
down_revision: Union[str, None] = '82c76ad97bc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('country', sa.String(length=10), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('competition_division_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('coach_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['competition_division_id'], ['competition_divisions.id']),
        sa.ForeignKeyConstraint(['coach_id'], ['coaches.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('bodyweight_kg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_sponsors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('tier', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('team_sponsors')
    op.drop_table('team_members')
    op.drop_table('teams')
