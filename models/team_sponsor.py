import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class TeamSponsor(Base):
    __tablename__ = "team_sponsors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    name = Column(String(200), nullable=False)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    # GENERAL (1 макс) / STANDARD (2 макс)
    tier = Column(String(20), nullable=False, default="STANDARD")
    team = relationship("Team", back_populates="sponsors")
