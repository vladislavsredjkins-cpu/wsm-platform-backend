import uuid
from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint("competition_division_id", "athlete_id", name="uq_participant_division_athlete"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_division_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_divisions.id", ondelete="CASCADE"),
        nullable=False,
    )

    athlete_id = Column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="CASCADE"),
        nullable=False,
    )

    bib_no = Column(Integer, nullable=True)
    bodyweight_kg = Column(Numeric, nullable=True)

    division = relationship("CompetitionDivision", back_populates="participants")
    athlete = relationship("Athlete")
