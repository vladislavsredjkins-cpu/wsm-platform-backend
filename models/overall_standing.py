import uuid

from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class OverallStanding(Base):
    __tablename__ = "overall_standings"
    __table_args__ = (
        UniqueConstraint(
            "competition_division_id",
            "participant_id",
            name="uq_overall_standings_division_participant",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_division_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_divisions.id", ondelete="CASCADE"),
        nullable=False,
    )

    participant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
    )

    total_points = Column(Numeric, nullable=False, default=0)
    place = Column(Integer, nullable=False)
    tie_break_value = Column(Numeric, nullable=True)

    division = relationship("CompetitionDivision")
    participant = relationship("Participant")
