from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import UserRole
from app.schemas.gemstone import GemstoneCreate, GemstoneUpdate, GemstoneOut
from app.api.deps import get_current_user, require_roles
from app.services import gemstone_service

router = APIRouter(prefix="/gemstones", tags=["Gemstones"])

@router.get("", response_model=Dict[str, Any])
def list_gemstones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    gemstone_type: Optional[str] = None,
    shape: Optional[str] = None,
    status: Optional[str] = None,
    location_id: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return gemstone_service.get_gemstones(
        db=db,
        skip=skip,
        limit=limit,
        gemstone_type=gemstone_type,
        shape=shape,
        status=status,
        location_id=location_id,
        query=query
    )

@router.post("", status_code=status.HTTP_201_CREATED)
def add_gemstone(
    gem_in: GemstoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return gemstone_service.create_gemstone(db, gem_in, current_user.id)

@router.put("/{gemstone_id}")
def edit_gemstone(
    gemstone_id: str,
    gem_in: GemstoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return gemstone_service.update_gemstone(db, gemstone_id, gem_in, current_user.id)
