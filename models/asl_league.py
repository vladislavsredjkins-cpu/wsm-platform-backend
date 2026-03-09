import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class ASLLeague(Base):
    __tablename__ = "asl_leagues"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)  # "Asian Strongman League 2026"
    season = Column(String(20), nullable=True)  # "2026"
    status = Column(String(20), default="active")  # active / finished
    divisions = relationship("ASLDivision", back_populates="league")
