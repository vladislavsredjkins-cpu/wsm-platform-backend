from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base


class CategoryScheme(Base):
    """
    Defines a category scheme used in competitions.

    Examples:
    - sex
    - weight_class
    - age_group
    - style
    """

    __tablename__ = "category_schemes"

    id = Column(Integer, primary_key=True, index=True)

    # unique key used in the system
    key = Column(String(50), unique=True, nullable=False)

    # human readable name
    name = Column(String(100), nullable=False)

    # optional description
    description = Column(String(255), nullable=True)

    # active flag
    is_active = Column(Boolean, default=True)
