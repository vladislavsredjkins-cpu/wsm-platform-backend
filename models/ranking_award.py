from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base


class RankingAward(Base):
    __tablename__ = "ranking_awards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    athlete_id = Column(UUID(as_uuid=True), nullable=False)
    competition_division_id = Column(UUID(as_uuid=True), nullable=False)

    overall_place = Column(Integer, nullable=False)
    p_event = Column(Float, nullable=False)
    q_effective_applied = Column(Float, nullable=False)
    s_awarded = Column(Float, nullable=False)

    policy_version = Column(String, nullable=False, default="1.2")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
