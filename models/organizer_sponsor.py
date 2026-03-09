import uuid
import datetime
from sqlalchemy import Column, String, Date, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class OrganizerSponsor(Base):
    __tablename__ = "organizer_sponsors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id"), nullable=False)
    name = Column(String(200), nullable=False)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    # Тиры: BRONZE / SILVER / GOLD / TITLE
    tier = Column(String(20), nullable=False, default="BRONZE")
    paid_until = Column(Date, nullable=True)
    price_paid = Column(Numeric(10, 2), nullable=True)
    organizer = relationship("Organizer", back_populates="sponsors")
