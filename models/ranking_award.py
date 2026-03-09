import uuid
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class RankingAward(Base):
    __tablename__ = "ranking_awards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False)
    overall_place = Column(Integer(), nullable=False)
    p_value = Column(Integer(), nullable=False)
    q_effective_applied = Column(Numeric(4, 2), nullable=False)
    s_awarded = Column(Numeric(8, 2), nullable=False)
    policy_version = Column(String(20), nullable=False, default="1.0")
    created_at = Column(DateTime(), nullable=False, default=datetime.datetime.utcnow)

    athlete = relationship("Athlete", back_populates="ranking_awards")
    division = relationship("CompetitionDivision", back_populates="ranking_awards")
    ranking_entries = relationship("RankingEntry", back_populates="ranking_award", cascade="all, delete-orphan")