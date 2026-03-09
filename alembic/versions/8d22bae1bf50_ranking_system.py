"""ranking system

Revision ID: 8d22bae1bf50
Revises: aba668a2512b
Create Date: 2026-03-08
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "8d22bae1bf50"
down_revision: Union[str, Sequence[str], None] = "aba668a2512b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass