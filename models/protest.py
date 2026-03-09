import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Protest(Base):
    __tablename__ = "protests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False)
    submitted_by = Column(UUID(as_uuid=True), nullable=False)
    description = Column(Text(), nullable=True)
    status = Column(String(50), nullable=False, default="SUBMITTED")
    resolution = Column(Text(), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    division = relationship("CompetitionDivision", back_populates="protests")