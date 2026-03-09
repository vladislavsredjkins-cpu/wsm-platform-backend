import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint("competition_division_id", "athlete_id", name="uq_participant_division_athlete"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    weight_in = Column(Numeric(6, 2), nullable=True)
    status = Column(String(50), nullable=False, default="REGISTERED")
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    division = relationship("CompetitionDivision", back_populates="participants")
    athlete = relationship("Athlete", back_populates="participants")
    discipline_results = relationship("DisciplineResult", back_populates="participant", cascade="all, delete-orphan")
    discipline_standings = relationship("DisciplineStanding", back_populates="participant", cascade="all, delete-orphan")
    overall_standings = relationship("OverallStanding", back_populates="participant", cascade="all, delete-orphan")