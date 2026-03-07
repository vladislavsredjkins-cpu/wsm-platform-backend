from sqlalchemy import Boolean, Column, Integer, JSON, String
from db.base import Base


class TeamRule(Base):
    __tablename__ = "team_rules"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    member_rules = Column(JSON, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
