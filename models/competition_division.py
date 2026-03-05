import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class CompetitionDivision(Base):
    __tablename__ = "competition_divisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # fixed values by platform terminology (store as String, validate in API later)
    division_key = Column(String, nullable=False)  # MEN | WOMEN | PARA
    format = Column(String, nullable=False)        # CLASSIC | PARA | RELAY | TEAM_BATTLE
    status = Column(String, nullable=False, default="DRAFT")  # lifecycle statuses

    competition = relationship("Competition", back_populates="divisions")

    disciplines = relationship(
        "CompetitionDiscipline",
        back_populates="division",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    participants = relationship(
        "Participant",
        back_populates="division",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
