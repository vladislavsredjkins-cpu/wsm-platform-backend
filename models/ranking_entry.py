import uuid
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class RankingEntry(Base):
    __tablename__ = "ranking_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    ranking_award_id = Column(UUID(as_uuid=True), ForeignKey("ranking_awards.id", ondelete="CASCADE"), nullable=False)
    division_key = Column(String(50), nullable=False)
    season_year = Column(Integer(), nullable=False)
    points = Column(Numeric(8, 2), nullable=False)
    awarded_at = Column(DateTime(), nullable=False, default=datetime.datetime.utcnow)

    athlete = relationship("Athlete", back_populates="ranking_entries")
    ranking_award = relationship("RankingAward", back_populates="ranking_entries")