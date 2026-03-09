import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    role = Column(String(50), nullable=False, default="REFEREE")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    athlete_id = Column(UUID(as_uuid=True), ForeignKey("athletes.id"), nullable=True)
    judge_id = Column(UUID(as_uuid=True), ForeignKey("judges.id"), nullable=True)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id"), nullable=True)