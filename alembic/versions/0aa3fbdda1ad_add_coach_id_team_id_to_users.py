"""add coach_id team_id to users

Revision ID: 0aa3fbdda1ad
Revises: fa277acb04bf
Create Date: 2026-03-12 07:58:07.200107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_pg

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0aa3fbdda1ad'
down_revision: Union[str, Sequence[str], None] = 'fa277acb04bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('coach_id', sa_pg.UUID(as_uuid=True), sa.ForeignKey('coaches.id'), nullable=True))
    op.add_column('users', sa.Column('team_id', sa_pg.UUID(as_uuid=True), sa.ForeignKey('teams.id'), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'team_id')
    op.drop_column('users', 'coach_id')
