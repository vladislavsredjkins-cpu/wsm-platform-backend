import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class ASLTeamDivision(Base):
    __tablename__ = "asl_team_divisions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    division_id = Column(UUID(as_uuid=True), ForeignKey("asl_divisions.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    division = relationship("ASLDivision", back_populates="teams")
    team = relationship("Team")
