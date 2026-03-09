import uuid
import datetime
from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from db.base import Base


class OverallStanding(Base):
    __tablename__ = "overall_standings"
    __table_args__ = (
        UniqueConstraint("competition_division_id", "participant_id", name="uq_overall_standings_division_participant"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    total_points = Column(Numeric(8, 2), nullable=False, default=0)
    overall_place = Column(Integer(), nullable=False)
    tiebreak_vector = Column(JSONB(), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    division = relationship("CompetitionDivision", back_populates="overall_standings")
    participant = relationship("Participant", back_populates="overall_standings")