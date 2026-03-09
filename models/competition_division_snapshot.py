import uuid
import datetime
from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from db.base import Base


class CompetitionDivisionSnapshot(Base):
    __tablename__ = "competition_division_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id", ondelete="CASCADE"), nullable=False)
    snapshot_data = Column(JSONB(), nullable=False)
    q_effective = Column(Numeric(4, 2), nullable=True)
    created_at = Column(DateTime(), nullable=False, default=datetime.datetime.utcnow)
    version = Column(Integer(), nullable=False, default=1)

    division = relationship("CompetitionDivision", back_populates="snapshots")