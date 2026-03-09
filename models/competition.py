import uuid
import datetime
from sqlalchemy import Column, String, Float, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    date_start = Column(Date, nullable=True)
    date_end = Column(Date, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    coefficient_q = Column(Float, nullable=False, default=1.0)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id"), nullable=True)

    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id"), nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    divisions = relationship("CompetitionDivision", back_populates="competition", cascade="all, delete-orphan")