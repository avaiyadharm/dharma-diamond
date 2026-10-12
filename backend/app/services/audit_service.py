import json
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_audit_event(
    db: Session,
    table_name: str,
    record_id: str,
    action: str,
    user_id: Optional[str] = None,
    old_values: Optional[Any] = None,
    new_values: Optional[Any] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    def serialize(val):
        if val is None:
            return None
        if isinstance(val, str):
            return val
        try:
            return json.dumps(val, default=str)
        except Exception:
            return str(val)

    audit_entry = AuditLog(
        table_name=table_name,
        record_id=str(record_id),
        action=action,
        user_id=user_id,
        old_values=serialize(old_values),
        new_values=serialize(new_values),
        description=description,
        ip_address=ip_address
    )
    db.add(audit_entry)
    return audit_entry
