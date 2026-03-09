import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=False)
    # ATHLETE_1 / ATHLETE_2 / RESERVE
    role = Column(String(20), nullable=False, default="ATHLETE_1")
    bodyweight_kg = Column(Numeric(5, 2), nullable=True)
    team = relationship("Team", back_populates="members")
    athlete = relationship("Athlete")
