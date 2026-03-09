import uuid
import datetime
from sqlalchemy import Column, String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country = Column(String(10), nullable=True)
    gender = Column(String(10), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)

    participants = relationship("Participant", back_populates="athlete")
    ranking_awards = relationship("RankingAward", back_populates="athlete")
    ranking_entries = relationship("RankingEntry", back_populates="athlete")
