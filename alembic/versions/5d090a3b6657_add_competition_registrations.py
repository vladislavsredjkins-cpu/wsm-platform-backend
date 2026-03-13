"""add competition_registrations

Revision ID: 5d090a3b6657
Revises: af39412a34fc
Create Date: 2026-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '5d090a3b6657'
down_revision = 'af39412a34fc'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('competition_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('division_key', sa.String(50), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('email', sa.String(200), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, server_default='PENDING'),
        sa.Column('reject_reason', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id']),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('competition_registrations')
