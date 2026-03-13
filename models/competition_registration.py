import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from db.base import Base

class CompetitionRegistration(Base):
    __tablename__ = "competition_registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=True)
    division_key = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING")
    reject_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
