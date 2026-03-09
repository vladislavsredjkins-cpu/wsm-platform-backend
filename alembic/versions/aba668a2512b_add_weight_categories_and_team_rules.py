"""add weight categories and team rules

Revision ID: aba668a2512b
Revises: accbf10b51fb
Create Date: 2026-03-07 20:10:56.292498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = 'aba668a2512b'
down_revision: Union[str, Sequence[str], None] = 'accbf10b51fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "weight_categories",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("division_type", sa.String(length=30), nullable=False),
        sa.Column("sex_scope", sa.String(length=30), nullable=False),
        sa.Column("weight_min_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("weight_max_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("is_open_upper", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_weight_categories_id", "weight_categories", ["id"])
    op.create_index("ix_weight_categories_code", "weight_categories", ["code"], unique=True)
    op.create_index("ix_weight_categories_division_type", "weight_categories", ["division_type"])
    op.create_index("ix_weight_categories_sex_scope", "weight_categories", ["sex_scope"])

    op.create_table(
        "team_rules",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("member_rules", sa.JSON(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_team_rules_id", "team_rules", ["id"])
    op.create_index("ix_team_rules_code", "team_rules", ["code"], unique=True)


def downgrade():
    op.drop_index("ix_team_rules_code", table_name="team_rules")
    op.drop_index("ix_team_rules_id", table_name="team_rules")
    op.drop_table("team_rules")

    op.drop_index("ix_weight_categories_sex_scope", table_name="weight_categories")
    op.drop_index("ix_weight_categories_division_type", table_name="weight_categories")
    op.drop_index("ix_weight_categories_code", table_name="weight_categories")
    op.drop_index("ix_weight_categories_id", table_name="weight_categories")
    op.drop_table("weight_categories")