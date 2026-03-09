"""sport tables

Revision ID: 0002_sport_tables
Revises: 0001_sport_core
Create Date: 2026-03-09
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "0002_sport_tables"
down_revision = "0001_sport_core"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("seasons",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table("athletes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("country_code", sa.String(3), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("is_para", sa.Boolean(), default=False),
        sa.Column("para_class", sa.String(20), nullable=True),
        sa.Column("certification_status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table("competitions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("competition_type", sa.String(100), nullable=False),
        sa.Column("track_type", sa.String(50), nullable=False),
        sa.Column("q_coefficient", sa.Numeric(4, 2), nullable=False),
        sa.Column("season_id", UUID(as_uuid=True), sa.ForeignKey("seasons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("country_code", sa.String(3), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table("competition_divisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_id", UUID(as_uuid=True), sa.ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("division_key", sa.String(50), nullable=False),
        sa.Column("format", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="OPEN"),
        sa.Column("is_locked", sa.Boolean(), default=False),
        sa.Column("locked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table("competition_disciplines",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_division_id", UUID(as_uuid=True), sa.ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("discipline_mode", sa.String(100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table("participants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_division_id", UUID(as_uuid=True), sa.ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("athlete_id", UUID(as_uuid=True), sa.ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weight_in", sa.Numeric(6, 2), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="REGISTERED"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("competition_division_id", "athlete_id", name="uq_participant_division_athlete"),
    )
    op.create_table("discipline_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_discipline_id", UUID(as_uuid=True), sa.ForeignKey("competition_disciplines.id", ondelete="CASCADE"), nullable=False),
        sa.Column("participant_id", UUID(as_uuid=True), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("result_value", sa.Numeric(10, 3), nullable=True),
        sa.Column("result_type", sa.String(50), nullable=True),
        sa.Column("is_zero", sa.Boolean(), default=False),
        sa.Column("payload", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("competition_discipline_id", "participant_id", name="uq_result_discipline_participant"),
    )
    op.create_table("discipline_standings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_discipline_id", UUID(as_uuid=True), sa.ForeignKey("competition_disciplines.id", ondelete="CASCADE"), nullable=False),
        sa.Column("participant_id", UUID(as_uuid=True), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("place", sa.Integer(), nullable=False),
        sa.Column("points_for_discipline", sa.Numeric(6, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("competition_discipline_id", "participant_id", name="uq_discipline_standings_discipline_participant"),
    )
    op.create_table("overall_standings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_division_id", UUID(as_uuid=True), sa.ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("participant_id", UUID(as_uuid=True), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("total_points", sa.Numeric(8, 2), nullable=False),
        sa.Column("overall_place", sa.Integer(), nullable=False),
        sa.Column("tiebreak_vector", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("competition_division_id", "participant_id", name="uq_overall_standings_division_participant"),
    )
    op.create_table("protests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_division_id", UUID(as_uuid=True), sa.ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submitted_by", UUID(as_uuid=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="SUBMITTED"),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table("competition_division_q",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_division_id", UUID(as_uuid=True), sa.ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("q_base", sa.Numeric(4, 2), nullable=False),
        sa.Column("q_effective", sa.Numeric(4, 2), nullable=False),
        sa.Column("policy_version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_table("competition_division_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_division_id", UUID(as_uuid=True), sa.ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_data", JSONB(), nullable=False),
        sa.Column("q_effective", sa.Numeric(4, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_table("ranking_awards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("athlete_id", UUID(as_uuid=True), sa.ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("competition_division_id", UUID(as_uuid=True), sa.ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_place", sa.Integer(), nullable=False),
        sa.Column("p_value", sa.Integer(), nullable=False),
        sa.Column("q_effective_applied", sa.Numeric(4, 2), nullable=False),
        sa.Column("s_awarded", sa.Numeric(8, 2), nullable=False),
        sa.Column("policy_version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table("ranking_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("athlete_id", UUID(as_uuid=True), sa.ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ranking_award_id", UUID(as_uuid=True), sa.ForeignKey("ranking_awards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("division_key", sa.String(50), nullable=False),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("points", sa.Numeric(8, 2), nullable=False),
        sa.Column("awarded_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("ranking_entries")
    op.drop_table("ranking_awards")
    op.drop_table("competition_division_snapshots")
    op.drop_table("competition_division_q")
    op.drop_table("protests")
    op.drop_table("overall_standings")
    op.drop_table("discipline_standings")
    op.drop_table("discipline_results")
    op.drop_table("participants")
    op.drop_table("competition_disciplines")
    op.drop_table("competition_divisions")
    op.drop_table("competitions")
    op.drop_table("athletes")
    op.drop_table("seasons")
