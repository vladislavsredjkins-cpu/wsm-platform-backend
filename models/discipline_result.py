import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class DisciplineResult(Base):
    __tablename__ = "discipline_results"
    __table_args__ = (
        UniqueConstraint(
            "competition_discipline_id",
            "participant_id",
            name="uq_discipline_result_discipline_participant",
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

    # универсальные поля под разные режимы
    primary_value = Column(Numeric, nullable=True)    # time sec / reps / meters / kg
    secondary_value = Column(Numeric, nullable=True)  # fallback metric

    status_flag = Column(String, nullable=False, default="OK")  # OK / DNF / DQ / DNS

    discipline = relationship("CompetitionDiscipline")
    participant = relationship("Participant")
