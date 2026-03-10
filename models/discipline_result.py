import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class DisciplineResult(Base):
    __tablename__ = "discipline_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_discipline_id = Column(UUID(as_uuid=True), ForeignKey("competition_disciplines.id"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    primary_value = Column(Numeric(10, 3), nullable=True)
    secondary_value = Column(Numeric(10, 3), nullable=True)
    reps = Column(Integer(), nullable=True)
    result_type = Column(String(20), nullable=True)  # TIME/WEIGHT/DISTANCE/REPS
    status_flag = Column(String(50), nullable=True)

    discipline = relationship("CompetitionDiscipline", back_populates="results")
    participant = relationship("Participant", back_populates="discipline_results")
