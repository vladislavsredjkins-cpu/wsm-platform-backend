"""Create competition_division_q table

Revision ID: 7c3dcd80517d
Revises: 8d22bae1bf50
Create Date: 2026-03-08 21:12:46.142137
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '7c3dcd80517d'
down_revision: Union[str, Sequence[str], None] = '8d22bae1bf50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass