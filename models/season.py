import uuid
from sqlalchemy import Column, Integer, Date, String
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base


class Season(Base):
    __tablename__ = "seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    year = Column(Integer, nullable=False)

    start_date = Column(Date)
    end_date = Column(Date)

    status = Column(String, default="ACTIVE")
