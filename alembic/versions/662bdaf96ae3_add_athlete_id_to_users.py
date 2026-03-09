"""add athlete_id to users

Revision ID: 662bdaf96ae3
Revises: 5c89e3d947f2
Create Date: 2026-03-09 17:50:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '662bdaf96ae3'
down_revision: Union[str, None] = '5c89e3d947f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('users_athlete_id_fkey', 'users', 'athletes', ['athlete_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('users_athlete_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'athlete_id')
