"""add judge_id organizer_id to users

Revision ID: ca1d65ccae32
Revises: 1ec0a20bbcaa
Create Date: 2026-03-09 18:55:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ca1d65ccae32'
down_revision: Union[str, None] = '1ec0a20bbcaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('judge_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('users_judge_id_fkey', 'users', 'judges', ['judge_id'], ['id'])
    op.create_foreign_key('users_organizer_id_fkey', 'users', 'organizers', ['organizer_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('users_organizer_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('users_judge_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'organizer_id')
    op.drop_column('users', 'judge_id')
