import uuid
import enum

from sqlalchemy import Column, ForeignKey, Enum, DateTime
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
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    LIVE = "LIVE"
    RESULTS_VALIDATED = "RESULTS_VALIDATED"
    LOCKED = "LOCKED"


class CompetitionDivision(Base):
    __tablename__ = "competition_divisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    division_key = Column(Enum(DivisionKey, name="divisionkey"), nullable=False)
    format = Column(Enum(CompetitionFormat, name="competitionformat"), nullable=False)
    status = Column(
        Enum(DivisionStatus, name="divisionstatus"),
        nullable=False,
        default=DivisionStatus.DRAFT,
    )

    approved_at = Column(DateTime, nullable=True)
    live_at = Column(DateTime, nullable=True)
    locked_at = Column(DateTime, nullable=True)

    competition = relationship("Competition", back_populates="divisions")

    disciplines = relationship(
        "CompetitionDiscipline",
        back_populates="division",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    participants = relationship(
        "Participant",
        back_populates="division",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
