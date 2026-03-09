"""add organizer_id location to competitions

Revision ID: 1ec0a20bbcaa
Revises: c6e55339a612
Create Date: 2026-03-09 18:50:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '1ec0a20bbcaa'
down_revision: Union[str, None] = 'c6e55339a612'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('competitions', sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('competitions', sa.Column('location', sa.String(), nullable=True))
    op.add_column('competitions', sa.Column('description', sa.Text(), nullable=True))
    op.create_foreign_key('competitions_organizer_id_fkey', 'competitions', 'organizers', ['organizer_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('competitions_organizer_id_fkey', 'competitions', type_='foreignkey')
    op.drop_column('competitions', 'description')
    op.drop_column('competitions', 'location')
    op.drop_column('competitions', 'organizer_id')
