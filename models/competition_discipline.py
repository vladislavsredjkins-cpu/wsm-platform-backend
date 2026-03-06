import uuid
import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
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

    competition_division_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_divisions.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_no = Column(Integer, nullable=False)
    discipline_name = Column(String, nullable=False)

    discipline_mode = Column(
        Enum(DisciplineMode, name="disciplinemode"),
        nullable=False,
    )

    time_cap_seconds = Column(Integer, nullable=True)
    lanes_per_heat = Column(Integer, nullable=True)
    track_length_meters = Column(Integer, nullable=True)

    division = relationship("CompetitionDivision", back_populates="disciplines")
