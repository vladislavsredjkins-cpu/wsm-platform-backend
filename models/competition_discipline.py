import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class CompetitionDiscipline(Base):
    __tablename__ = "competition_disciplines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_division_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_divisions.id"),
        nullable=False
    )

    order_no = Column(Integer, nullable=False)

    discipline_name = Column(String, nullable=False)

    discipline_mode = Column(String, nullable=False)

    time_cap_seconds = Column(Integer)

    lanes_count = Column(Integer)

    division = relationship("CompetitionDivision")
