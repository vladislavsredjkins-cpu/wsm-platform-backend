import uuid
from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_division_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_divisions.id"),
        nullable=False
    )

    athlete_id = Column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id"),
        nullable=False
    )

    bib_no = Column(Integer)

    bodyweight_kg = Column(Numeric)

    division = relationship("CompetitionDivision")

    athlete = relationship("Athlete")
