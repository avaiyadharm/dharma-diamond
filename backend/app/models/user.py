from sqlalchemy import Column, String, Boolean, DateTime
from app.models.base import TimeStampedModel

class User(TimeStampedModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), default="sales_staff", nullable=False)  # admin, inventory_manager, sales_staff, accountant, read_only
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
