from sqlalchemy import Column, String, Integer, Date, ForeignKey
from db.base import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)