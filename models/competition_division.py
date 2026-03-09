import uuid
import datetime
import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class DivisionKey(str, enum.Enum):
    MEN = "MEN"
    WOMEN = "WOMEN"
    PARA = "PARA"


class CompetitionFormat(str, enum.Enum):
    CLASSIC = "CLASSIC"
    PARA = "PARA"
    RELAY = "RELAY"
    TEAM_BATTLE = "TEAM_BATTLE"


class DivisionStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESULTS_VALIDATED = "RESULTS_VALIDATED"
    LOCKED = "LOCKED"


class CompetitionDivision(Base):
    __tablename__ = "competition_divisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
    division_key = Column(String(50), nullable=False)
    format = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="OPEN")
    is_locked = Column(Boolean(), default=False)
    locked_at = Column(DateTime(), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    competition = relationship("Competition", back_populates="divisions")
    disciplines = relationship("CompetitionDiscipline", back_populates="division", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="division", cascade="all, delete-orphan")
    overall_standings = relationship("OverallStanding", back_populates="division", cascade="all, delete-orphan")
    protests = relationship("Protest", back_populates="division", cascade="all, delete-orphan")
    division_q = relationship("CompetitionDivisionQ", back_populates="division", uselist=False)
    snapshots = relationship("CompetitionDivisionSnapshot", back_populates="division", cascade="all, delete-orphan")
    ranking_awards = relationship("RankingAward", back_populates="division", cascade="all, delete-orphan")