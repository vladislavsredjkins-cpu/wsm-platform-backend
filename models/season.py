import uuid
import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class Season(Base):
    __tablename__ = "seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year = Column(Integer(), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.utcnow)

    