import uuid
import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base

class Organizer(Base):
    __tablename__ = "organizers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)

    # Тип: federation / club / person
    type = Column(String(20), nullable=False, default="person")

    # Название федерации/клуба или ФИО
    name = Column(String(300), nullable=False)

    country = Column(String(10), nullable=True)
    city = Column(String(100), nullable=True)
    photo_url = Column(String(500), nullable=True)   # фото или лого
    website = Column(String(500), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    instagram = Column(String(100), nullable=True)

    sponsors = relationship("OrganizerSponsor", back_populates="organizer")
