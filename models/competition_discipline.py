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
        ForeignKey("competition_divisions.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_no = Column(Integer, nullable=False)
    discipline_name = Column(String, nullable=False)

    # fixed modes per platform spec (store as String; validate in API)
    discipline_mode = Column(String, nullable=False)

    time_cap_seconds = Column(Integer, nullable=True)
    lanes_per_heat = Column(Integer, nullable=True)
    track_length_meters = Column(Integer, nullable=True)

    division = relationship("CompetitionDivision", back_populates="disciplines")
