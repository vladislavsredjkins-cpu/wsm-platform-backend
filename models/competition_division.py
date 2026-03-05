import uuid
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base
import enum


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
        ForeignKey("competitions.id"),
        nullable=False
    )

    division_key = Column(Enum(DivisionKey), nullable=False)

    format = Column(Enum(CompetitionFormat), nullable=False)

    status = Column(
        Enum(DivisionStatus),
        default=DivisionStatus.DRAFT,
        nullable=False
    )

    competition = relationship("Competition", back_populates="divisions")
