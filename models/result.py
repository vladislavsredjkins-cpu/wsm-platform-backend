import uuid

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=False)

    place = Column(Integer, nullable=False)  # 1..N
    status = Column(String, nullable=False, default="approved")  # pending/approved/rejected
