from sqlalchemy import Boolean, Column, Integer, Numeric, String
from db.base import Base


class WeightCategory(Base):
    __tablename__ = "weight_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    division_type = Column(String(30), nullable=False, index=True)
    sex_scope = Column(String(30), nullable=False, index=True)
    weight_min_kg = Column(Numeric(6, 2), nullable=True)
    weight_max_kg = Column(Numeric(6, 2), nullable=True)
    is_open_upper = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    age_group = Column(String(30), nullable=False, default="SENIOR", index=True)
    is_active = Column(Boolean, default=True, nullable=False)
