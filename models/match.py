import uuid
import datetime
from sqlalchemy import Column, String, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class Match(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id"), nullable=False)
    home_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    match_date = Column(Date, nullable=True)
    home_score = Column(Integer, default=0)  # 0-5 дисциплин
    away_score = Column(Integer, default=0)
    status = Column(String(20), default="scheduled")  # scheduled / completed / cancelled
    round_number = Column(Integer, nullable=True)  # 1-6 (double round robin)
    discipline_results = relationship("MatchDisciplineResult", back_populates="match")
