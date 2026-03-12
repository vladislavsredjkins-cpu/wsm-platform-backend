"""add competition_sponsors table
Revision ID: 97f7bc2fbd54
Revises: 8a990865ff68
Create Date: 2026-03-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '97f7bc2fbd54'
down_revision = '8a990865ff68'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('competition_sponsors',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('competition_id', UUID(as_uuid=True), sa.ForeignKey('competitions.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('tier', sa.String(), nullable=True, server_default='FREE'),
    )

def downgrade() -> None:
    op.drop_table('competition_sponsors')
