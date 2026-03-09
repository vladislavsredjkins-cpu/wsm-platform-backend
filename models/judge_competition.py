import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class JudgeCompetition(Base):
    __tablename__ = "judge_competitions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    judge_id = Column(UUID(as_uuid=True), ForeignKey("judges.id"), nullable=False)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    role = Column(String(100), nullable=True)  # head judge / judge / technical delegate
    judge = relationship("Judge", back_populates="competition_assignments")
