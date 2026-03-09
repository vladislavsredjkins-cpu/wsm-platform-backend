import uuid
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class CoachCertificate(Base):
    __tablename__ = "coach_certificates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.id"), nullable=False)
    title = Column(String(300), nullable=False)
    issued_by = Column(String(300), nullable=True)
    issued_date = Column(Date, nullable=True)
    expires_date = Column(Date, nullable=True)
    file_url = Column(String(500), nullable=True)
    coach = relationship("Coach", back_populates="certificates")
