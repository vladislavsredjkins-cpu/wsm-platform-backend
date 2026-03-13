import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class MatchDisciplineResult(Base):
    __tablename__ = "match_discipline_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    discipline_name = Column(String(100), nullable=False)
    home_result = Column(Numeric(8, 2), nullable=True)  # результат (кг, сек, см)
    away_result = Column(Numeric(8, 2), nullable=True)
    # home / away / draw
    winner = Column(String(10), nullable=True)
    result_type = Column(String(20), default='higher_wins')  # higher_wins / lower_wins
    unit = Column(String(10), nullable=True)  # kg, sec, reps, m
    match = relationship("Match", back_populates="discipline_results")
