import uuid
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base


class RankingSnapshot(Base):
    __tablename__ = "ranking_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    season_year = Column(Integer, nullable=False)

    division_key = Column(String, nullable=False)
    format = Column(String, nullable=False)

    athlete_id = Column(UUID(as_uuid=True), nullable=False)

    points = Column(Numeric, nullable=False)
    place = Column(Integer, nullable=False)
