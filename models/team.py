import uuid
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    logo_url = Column(String(500), nullable=True)
    team_photo_url = Column(String(500), nullable=True)
    country = Column(String(10), nullable=True)
    email = Column(String(200), nullable=True)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id"), nullable=True)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.id"), nullable=True)
    status = Column(String(20), default="pending")  # pending / approved / rejected
    members = relationship("TeamMember", back_populates="team")
    sponsors = relationship("TeamSponsor", back_populates="team")
