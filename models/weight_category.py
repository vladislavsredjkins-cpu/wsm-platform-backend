from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class WeightCategory(Base):
    __tablename__ = "weight_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    division_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    sex_scope: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    weight_min_kg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    weight_max_kg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    is_open_upper: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
