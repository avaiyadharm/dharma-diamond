from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class AuditLog(TimeStampedModel):
    __tablename__ = "audit_logs"

    table_name = Column(String(64), index=True, nullable=False)
    record_id = Column(String(64), index=True, nullable=False)
    action = Column(String(32), index=True, nullable=False)  # CREATE, UPDATE, DELETE, SALE, CANCEL, ADJUST
    old_values = Column(Text, nullable=True)  # JSON formatted snapshot
    new_values = Column(Text, nullable=True)  # JSON formatted snapshot
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)

    user = relationship("User", foreign_keys=[user_id])
