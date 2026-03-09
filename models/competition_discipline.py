import uuid
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class CompetitionDiscipline(Base):
    __tablename__ = "competition_disciplines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_division_id = Column(UUID(as_uuid=True), ForeignKey("competition_divisions.id"), nullable=False)
    order_no = Column(Integer(), nullable=True)
    discipline_name = Column(String(200), nullable=False)
    discipline_mode = Column(String(50), nullable=True)
    time_cap_seconds = Column(Integer(), nullable=True)
    lanes_count = Column(Integer(), nullable=True)
    lanes_per_heat = Column(Integer(), nullable=True)
    track_length_meters = Column(Numeric(10, 2), nullable=True)

    division = relationship("CompetitionDivision", back_populates="disciplines")
    results = relationship("DisciplineResult", back_populates="discipline", cascade="all, delete-orphan")
    standings = relationship("DisciplineStanding", back_populates="discipline", cascade="all, delete-orphan")
