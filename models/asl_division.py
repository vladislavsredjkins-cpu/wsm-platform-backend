import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class ASLDivision(Base):
    __tablename__ = "asl_divisions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("asl_leagues.id"), nullable=False)
    name = Column(String(200), nullable=False)  # "East Division", "West Division"
    region = Column(String(100), nullable=True)  # "East Asia", "South Asia"
    max_teams = Column(Integer, default=4)
    league = relationship("ASLLeague", back_populates="divisions")
    teams = relationship("ASLTeamDivision", back_populates="division")
