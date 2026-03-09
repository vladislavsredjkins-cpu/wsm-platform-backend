import uuid
from sqlalchemy import Column, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from db.base import Base

division_key_enum = ENUM(
    'MEN', 'WOMEN', 'PARA',
    'MEN_YOUTH_16', 'WOMEN_YOUTH_16',
    'MEN_YOUTH_18', 'WOMEN_YOUTH_18',
    'MEN_JUNIOR', 'WOMEN_JUNIOR',
    'MEN_SENIOR', 'WOMEN_SENIOR',
    'MEN_MASTERS_40', 'WOMEN_MASTERS_40',
    'MEN_MASTERS_50', 'WOMEN_MASTERS_50',
    'PARA_MEN', 'PARA_WOMEN',
    name='divisionkey', create_type=False
)
format_enum = ENUM('CLASSIC', 'PARA', 'RELAY', 'TEAM_BATTLE', name='competitionformat', create_type=False)
status_enum = ENUM('DRAFT', 'SUBMITTED', 'APPROVED', 'LIVE', 'RESULTS_VALIDATED', 'LOCKED', name='divisionstatus', create_type=False)


class CompetitionDivision(Base):
    __tablename__ = "competition_divisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    division_key = Column(division_key_enum, nullable=False)
    format = Column(format_enum, nullable=True)
    status = Column(status_enum, default="DRAFT")
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
