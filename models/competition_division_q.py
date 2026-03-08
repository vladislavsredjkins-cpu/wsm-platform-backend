from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

class CompetitionDivisionQ(Base):
    __tablename__ = "competition_division_q"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey('competition_divisions.id'), nullable=False)
    q_base = Column(Numeric, nullable=False)
    q_effective = Column(Numeric, nullable=False)
    calculated_at = Column(DateTime, nullable=False)
    calculation_method = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)

    competition_division = relationship("CompetitionDivision", back_populates="division_q")
