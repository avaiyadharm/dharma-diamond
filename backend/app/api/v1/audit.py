from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogOut
from app.api.deps import get_current_admin

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogOut])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    table_name: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    query = db.query(AuditLog)
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for log in logs:
        results.append({
            "id": log.id,
            "table_name": log.table_name,
            "record_id": log.record_id,
            "action": log.action,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "user_id": log.user_id,
            "user_name": log.user.full_name if log.user else None,
            "ip_address": log.ip_address,
            "description": log.description,
            "created_at": log.created_at
        })
    return results
