import uuid
from sqlalchemy import Column, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id"), nullable=False)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=False)
    bib_no = Column(Integer(), nullable=True)
    bodyweight_kg = Column(Numeric(6, 2), nullable=True)

    division = relationship("CompetitionDivision", back_populates="participants")
    athlete = relationship("Athlete", back_populates="participants")
    discipline_results = relationship("DisciplineResult", back_populates="participant", cascade="all, delete-orphan")
    discipline_standings = relationship("DisciplineStanding", back_populates="participant", cascade="all, delete-orphan")
    overall_standings = relationship("OverallStanding", back_populates="participant", cascade="all, delete-orphan")
