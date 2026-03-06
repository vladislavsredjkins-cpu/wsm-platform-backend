import uuid

from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class DisciplineStanding(Base):
    __tablename__ = "discipline_standings"
    __table_args__ = (
        UniqueConstraint(
            "competition_discipline_id",
            "participant_id",
            name="uq_discipline_standings_discipline_participant",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_discipline_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_disciplines.id", ondelete="CASCADE"),
        nullable=False,
    )

    participant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
    )

    place = Column(Integer, nullable=False)
    points_for_discipline = Column(Numeric, nullable=False, default=0)

    discipline = relationship("CompetitionDiscipline")
    participant = relationship("Participant")
