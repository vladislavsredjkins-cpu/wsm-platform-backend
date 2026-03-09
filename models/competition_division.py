import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class CompetitionDivision(Base):
    __tablename__ = "competition_divisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    division_key = Column(String(100), nullable=False)
    format = Column(String(50), nullable=True)
    status = Column(String(50), default="OPEN")
    approved_at = Column(DateTime(), nullable=True)
    live_at = Column(DateTime(), nullable=True)
    locked_at = Column(DateTime(), nullable=True)
    q_effective = Column(Numeric(10, 2), nullable=True)

    competition = relationship("Competition", back_populates="divisions")
    disciplines = relationship("CompetitionDiscipline", back_populates="division", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="division", cascade="all, delete-orphan")
    overall_standings = relationship("OverallStanding", back_populates="division", cascade="all, delete-orphan")
    protests = relationship("Protest", back_populates="division", cascade="all, delete-orphan")
    division_q = relationship("CompetitionDivisionQ", back_populates="division", uselist=False)
    snapshots = relationship("CompetitionDivisionSnapshot", back_populates="division", cascade="all, delete-orphan")
    ranking_awards = relationship("RankingAward", back_populates="division", cascade="all, delete-orphan")
