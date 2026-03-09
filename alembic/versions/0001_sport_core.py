"""sport core tables

Revision ID: 0001_sport_core
Revises: 7c3dcd80517d
Create Date: 2026-03-09
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "0001_sport_core"
down_revision = "7c3dcd80517d"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
