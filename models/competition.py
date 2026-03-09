import uuid
import datetime
from sqlalchemy import Column, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    competition_type = Column(String(100), nullable=False)
    track_type = Column(String(50), nullable=False)
    q_coefficient = Column(Numeric(4, 2), nullable=False)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id", ondelete="SET NULL"), nullable=True)
    country_code = Column(String(3), nullable=True)
    city = Column(String(100), nullable=True)
    start_date = Column(Date(), nullable=True)
    end_date = Column(Date(), nullable=True)
    status = Column(String(50), nullable=False, default="DRAFT")
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    season = relationship("Season", back_populates="competitions")
    divisions = relationship("CompetitionDivision", back_populates="competition", cascade="all, delete-orphan")