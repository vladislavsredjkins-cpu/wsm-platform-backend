import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base

class CompetitionSponsor(Base):
    __tablename__ = "competition_sponsors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    name = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    tier = Column(String, default='FREE')  # PAID or FREE
    mc_text = Column(String, nullable=True)
