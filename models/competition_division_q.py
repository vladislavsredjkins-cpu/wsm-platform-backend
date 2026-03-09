import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class CompetitionDivisionQ(Base):
    __tablename__ = "competition_division_q"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False, unique=True)
    q_base = Column(Numeric(4, 2), nullable=False)
    q_effective = Column(Numeric(4, 2), nullable=False)
    policy_version = Column(String(20), nullable=False, default="1.0")
    confirmed_at = Column(DateTime(), nullable=True)
    confirmed_by = Column(UUID(as_uuid=True), nullable=True)

    division = relationship("CompetitionDivision", back_populates="division_q")