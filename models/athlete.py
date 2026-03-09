import uuid
from sqlalchemy import Column, String, Boolean, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base
import datetime


class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country_code = Column(String(3), nullable=True)
    birth_date = Column(Date(), nullable=True)
    gender = Column(String(10), nullable=True)
    is_para = Column(Boolean(), default=False)
    para_class = Column(String(20), nullable=True)
    certification_status = Column(String(50), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    participants = relationship("Participant", back_populates="athlete")
    ranking_awards = relationship("RankingAward", back_populates="athlete")
    ranking_entries = relationship("RankingEntry", back_populates="athlete")