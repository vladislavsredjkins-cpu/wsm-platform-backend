"""add banner status type to competitions

Revision ID: 8a990865ff68
Revises: 0aa3fbdda1ad
Create Date: 2026-03-12

"""
from alembic import op
import sqlalchemy as sa

revision = '8a990865ff68'
down_revision = '0aa3fbdda1ad'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('competitions', sa.Column('banner_url', sa.String(), nullable=True))
    op.add_column('competitions', sa.Column('status', sa.String(), nullable=True, server_default='DRAFT'))
    op.add_column('competitions', sa.Column('competition_type', sa.String(), nullable=True))
    op.add_column('competitions', sa.Column('organizer_email', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('competitions', 'organizer_email')
    op.drop_column('competitions', 'competition_type')
    op.drop_column('competitions', 'status')
    op.drop_column('competitions', 'banner_url')
