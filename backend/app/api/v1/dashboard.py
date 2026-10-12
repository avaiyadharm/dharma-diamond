from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=Dict[str, Any])
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return dashboard_service.get_dashboard_metrics(db)
