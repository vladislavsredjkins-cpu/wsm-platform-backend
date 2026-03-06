import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from db.base import Base


class Protest(Base):
    __tablename__ = "protests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_id = Column(UUID(as_uuid=True), nullable=False)

    athlete_id = Column(UUID(as_uuid=True), nullable=False)

    reason = Column(String, nullable=False)

    status = Column(String, default="SUBMITTED")

    created_at = Column(DateTime, default=datetime.utcnow)
