import uuid
from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base


class CompetitionClass(Base):
    __tablename__ = "competition_classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)

    coefficient_q = Column(Numeric, nullable=False)
