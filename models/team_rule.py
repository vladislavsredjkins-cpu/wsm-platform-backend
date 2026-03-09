from sqlalchemy import Boolean, Column, Integer, Numeric, String
from db.base import Base


class TeamRule(Base):
    __tablename__ = "team_rules"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)

    athletes_per_team = Column(Integer, nullable=False)

    athlete1_max_weight = Column(Numeric(6, 2), nullable=True)
    athlete2_min_weight = Column(Numeric(6, 2), nullable=True)

    description = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
