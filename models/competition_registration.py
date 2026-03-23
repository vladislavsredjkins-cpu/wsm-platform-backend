import uuid
import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class CompetitionRegistration(Base):
    __tablename__ = "competition_registrations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=False)
    athlete_email = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)  # stripe / crypto
    payment_id = Column(String, nullable=True)       # stripe session_id or nowpayments payment_id
    amount_eur = Column(Float, nullable=True)
    status = Column(String, default="PENDING")       # PENDING / PAID / CANCELLED
    non_refundable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
