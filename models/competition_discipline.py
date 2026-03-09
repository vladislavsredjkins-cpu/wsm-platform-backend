import uuid
import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class DisciplineMode(str, enum.Enum):
    TIME_WITH_DISTANCE_FALLBACK = "TIME_WITH_DISTANCE_FALLBACK"
    AMRAP_REPS = "AMRAP_REPS"
    AMRAP_DISTANCE = "AMRAP_DISTANCE"
    MAX_WEIGHT_WITHIN_CAP = "MAX_WEIGHT_WITHIN_CAP"
    RELAY_DUAL_METRIC = "RELAY_DUAL_METRIC"


class CompetitionDiscipline(Base):
    __tablename__ = "competition_disciplines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    discipline_mode = Column(String(100), nullable=False)
    sort_order = Column(Integer(), nullable=False, default=0)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    division = relationship("CompetitionDivision", back_populates="disciplines")
    results = relationship("DisciplineResult", back_populates="discipline", cascade="all, delete-orphan")
    standings = relationship("DisciplineStanding", back_populates="discipline", cascade="all, delete-orphan")