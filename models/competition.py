import uuid
from datetime import date

from sqlalchemy import Column, String, Date, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)

    city = Column(String, nullable=True)
    country = Column(String, nullable=True)

    coefficient_q = Column(Float, nullable=False, default=1.0)

    class_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_classes.id"),
        nullable=True,
    )

    season_id = Column(
        UUID(as_uuid=True),
        ForeignKey("seasons.id"),
        nullable=True,
    )

    divisions = relationship(
        "CompetitionDivision",
        back_populates="competition",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
