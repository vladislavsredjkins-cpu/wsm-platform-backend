import uuid
import datetime
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class JudgeCertificate(Base):
    __tablename__ = "judge_certificates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    judge_id = Column(UUID(as_uuid=True), ForeignKey("judges.id"), nullable=False)
    title = Column(String(300), nullable=False)
    issued_by = Column(String(300), nullable=True)
    issued_date = Column(Date, nullable=True)
    expires_date = Column(Date, nullable=True)
    file_url = Column(String(500), nullable=True)
    certificate_number = Column(String(100), nullable=True)
    programme_code = Column(String(50), nullable=True)
    verify_url = Column(String(500), nullable=True)
    verify_hash = Column(String(500), nullable=True)
    course_name = Column(String(300), nullable=True)
    status = Column(String(20), default='active')
    judge = relationship("Judge", back_populates="certificates")
