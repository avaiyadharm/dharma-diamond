from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AuditLogOut(BaseModel):
    id: str
    table_name: str
    record_id: str
    action: str
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    ip_address: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
