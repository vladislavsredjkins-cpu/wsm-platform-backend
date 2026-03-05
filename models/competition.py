import uuid
from datetime import date

from sqlalchemy import Column, String, Date, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship  # ✅ add

from db.base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)

    city = Column(String, nullable=True)
    country = Column(String, nullable=True)

    # Tournament Coefficient Q
    coefficient_q = Column(Float, nullable=False, default=1.0)

    # ✅ Stage 2 relation
    divisions = relationship(
        "CompetitionDivision",
        back_populates="competition",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
