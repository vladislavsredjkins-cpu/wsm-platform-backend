import uuid
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class TeamStanding(Base):
    __tablename__ = "team_standings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asl_division_id = Column(UUID(as_uuid=True), ForeignKey("asl_divisions.id"), nullable=True)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id"), nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    disciplines_won = Column(Integer, default=0)
    disciplines_lost = Column(Integer, default=0)
    points = Column(Integer, default=0)  # 3 за победу, 1 за ничью, 0 за поражение
    team = relationship("Team")
