"""add asl league division tables

Revision ID: f8e456351102
Revises: f172f6a15f4a
Create Date: 2026-03-09 20:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f8e456351102'
down_revision: Union[str, None] = 'f172f6a15f4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('asl_leagues',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('season', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('asl_divisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('league_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('max_teams', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['league_id'], ['asl_leagues.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('asl_team_divisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('division_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['division_id'], ['asl_divisions.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('matches', sa.Column('asl_division_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'matches', 'asl_divisions', ['asl_division_id'], ['id'])
    op.alter_column('matches', 'competition_division_id', nullable=True)
    op.add_column('team_standings', sa.Column('asl_division_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'team_standings', 'asl_divisions', ['asl_division_id'], ['id'])
    op.alter_column('team_standings', 'competition_division_id', nullable=True)

def downgrade() -> None:
    op.drop_column('team_standings', 'asl_division_id')
    op.drop_column('matches', 'asl_division_id')
    op.drop_table('asl_team_divisions')
    op.drop_table('asl_divisions')
    op.drop_table('asl_leagues')
