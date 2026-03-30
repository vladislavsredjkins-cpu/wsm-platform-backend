import uuid
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base
import enum


class DisciplineMode(str, enum.Enum):
    AMRAP_REPS = "AMRAP_REPS"
    AMRAP_DISTANCE = "AMRAP_DISTANCE"
    TIME_WITH_DISTANCE_FALLBACK = "TIME_WITH_DISTANCE_FALLBACK"
    MAX_WEIGHT_WITHIN_CAP = "MAX_WEIGHT_WITHIN_CAP"
    RELAY_DUAL_METRIC = "RELAY_DUAL_METRIC"
    STATIC_HOLD_TIME = "STATIC_HOLD_TIME"


class CompetitionDiscipline(Base):
    __tablename__ = "competition_disciplines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id"), nullable=True)
    events_division_id = Column(UUID(as_uuid=True), ForeignKey("events_divisions.id"), nullable=True)
    order_no = Column(Integer, nullable=True)
    discipline_name = Column(String(200), nullable=False)
    discipline_mode = Column(String(50), nullable=False, default="AMRAP_REPS")
    time_cap_seconds = Column(Integer, nullable=True)
    lanes_count = Column(Integer, nullable=True)
    lanes_per_heat = Column(Integer, nullable=True)
    track_length_meters = Column(Numeric(6, 2), nullable=True)
    implement_weight = Column(String(200), nullable=True)
    result_unit = Column(String(20), nullable=True)  # kg/sec/m/reps
    is_final = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)

    division = relationship("CompetitionDivision", back_populates="disciplines")
    results = relationship("DisciplineResult", back_populates="discipline")
    standings = relationship("DisciplineStanding", back_populates="discipline")
