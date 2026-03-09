import uuid
import datetime
from sqlalchemy import Column, String, Date, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class Judge(Base):
    __tablename__ = "judges"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country = Column(String(10), nullable=True)
    gender = Column(String(10), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    photo_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    level = Column(String(50), nullable=True)
    # Уровни судей:
    # NATIONAL_1   — Национальный судья 1 категории
    # NATIONAL_2   — Национальный судья 2 категории
    # INTERNATIONAL_3 — Международный судья 3 категории
    # INTERNATIONAL_4 — Международный судья 4 категории (высший)
    instagram = Column(String(100), nullable=True)
    certificates = relationship("JudgeCertificate", back_populates="judge")
    competition_assignments = relationship("JudgeCompetition", back_populates="judge")
