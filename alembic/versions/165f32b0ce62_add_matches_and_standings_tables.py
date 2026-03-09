"""add matches and standings tables

Revision ID: 165f32b0ce62
Revises: 9be4784da290
Create Date: 2026-03-09 19:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '165f32b0ce62'
down_revision: Union[str, None] = '9be4784da290'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competition_division_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_date', sa.Date(), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=True),
        sa.Column('away_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('round_number', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['competition_division_id'], ['competition_divisions.id']),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('match_discipline_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discipline_name', sa.String(length=100), nullable=False),
        sa.Column('home_result', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('away_result', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('winner', sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_standings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competition_division_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('matches_played', sa.Integer(), nullable=True),
        sa.Column('wins', sa.Integer(), nullable=True),
        sa.Column('losses', sa.Integer(), nullable=True),
        sa.Column('disciplines_won', sa.Integer(), nullable=True),
        sa.Column('disciplines_lost', sa.Integer(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['competition_division_id'], ['competition_divisions.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('team_standings')
    op.drop_table('match_discipline_results')
    op.drop_table('matches')
