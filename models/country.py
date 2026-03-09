from sqlalchemy import Column, String, Integer
from db.base import Base

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=True)
