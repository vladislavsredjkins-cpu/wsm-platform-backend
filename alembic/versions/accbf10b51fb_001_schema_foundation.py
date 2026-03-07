"""001_schema_foundation

Revision ID: accbf10b51fb
Revises:
Create Date: 2026-03-07 10:41:55.646254

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "accbf10b51fb"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=3), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )

    op.create_table(
        "federations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("country_id", sa.Integer(), sa.ForeignKey("countries.id")),
    )

    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(length=100)),
        sa.Column("last_name", sa.String(length=100)),
        sa.Column("birth_date", sa.Date()),
        sa.Column("country_id", sa.Integer(), sa.ForeignKey("countries.id")),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255)),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("persons.id")),
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id")),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("roles")
    op.drop_table("users")
    op.drop_table("persons")
    op.drop_table("federations")
    op.drop_table("countries")