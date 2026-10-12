from sqlalchemy import Column, String, Boolean, Text
from app.models.base import TimeStampedModel

class Location(TimeStampedModel):
    __tablename__ = "inventory_locations"

    code = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
