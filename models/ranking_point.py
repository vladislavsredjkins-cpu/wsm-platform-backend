import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class RankingPoint(Base):
    __tablename__ = "ranking_points"
    __table_args__ = (
        UniqueConstraint(
            "competition_id",
            "division_id",
            "athlete_id",
            name="uq_ranking_points_comp_div_athlete",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    season_year = Column(Integer, nullable=False)

    competition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    division_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competition_divisions.id", ondelete="CASCADE"),
        nullable=False,
    )

    athlete_id = Column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="CASCADE"),
        nullable=False,
    )

    division_key = Column(String, nullable=False)  # MEN/WOMEN/PARA
    format = Column(String, nullable=False)        # CLASSIC/PARA/RELAY/TEAM_BATTLE

    # начисленные очки (после умножения на coefficient_q)
    points = Column(Numeric, nullable=False, default=0)

    competition = relationship("Competition")
    division = relationship("CompetitionDivision")
    athlete = relationship("Athlete")
