import uuid
import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from db.base import Base


class DisciplineResult(Base):
    __tablename__ = "discipline_results"
    __table_args__ = (
        UniqueConstraint("competition_discipline_id", "participant_id", name="uq_result_discipline_participant"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_discipline_id = Column(UUID(as_uuid=True), ForeignKey("competition_disciplines.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    result_value = Column(Numeric(10, 3), nullable=True)
    result_type = Column(String(50), nullable=True)
    is_zero = Column(Boolean(), default=False)
    payload = Column(JSONB(), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    discipline = relationship("CompetitionDiscipline", back_populates="results")
    participant = relationship("Participant", back_populates="discipline_results")