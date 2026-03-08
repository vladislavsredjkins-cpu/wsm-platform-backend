from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base


class RankingEntry(Base):
    __tablename__ = "ranking_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    athlete_id = Column(UUID(as_uuid=True), nullable=False)
    competition_division_id = Column(UUID(as_uuid=True), nullable=False)

    points_awarded = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    q_value = Column(Float, nullable=False)

    formula_version = Column(String, nullable=False, default="1.2")
    awarded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
