from decimal import Decimal
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import UserRole
from app.schemas.diamond import (
    DiamondCreate, DiamondUpdate, DiamondOut,
    DiamondAdjustment, DiamondReservationRequest
)
from app.api.deps import get_current_user, require_roles
from app.services import diamond_service

router = APIRouter(prefix="/diamonds", tags=["Diamonds"])

@router.get("", response_model=Dict[str, Any])
def list_diamonds(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    query: Optional[str] = None,
    shape: Optional[str] = None,
    color_grade: Optional[str] = None,
    clarity_grade: Optional[str] = None,
    min_carat: Optional[Decimal] = None,
    max_carat: Optional[Decimal] = None,
    status: Optional[str] = None,
    location_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    diamond_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return diamond_service.get_diamonds(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
        shape=shape,
        color_grade=color_grade,
        clarity_grade=clarity_grade,
        min_carat=min_carat,
        max_carat=max_carat,
        status=status,
        location_id=location_id,
        supplier_id=supplier_id,
        diamond_type=diamond_type
    )

@router.post("", status_code=status.HTTP_201_CREATED)
def add_diamond(
    diamond_in: DiamondCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return diamond_service.create_diamond(db, diamond_in, current_user.id)

@router.get("/{diamond_id}")
def get_diamond(
    diamond_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diamond = diamond_service.get_diamond_by_id(db, diamond_id)
    if not diamond:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diamond not found")
    
    return {
        "id": diamond.id,
        "sku": diamond.sku,
        "is_parcel": diamond.is_parcel,
        "lot_number": diamond.lot_number,
        "shape": diamond.shape,
        "carat_weight": diamond.carat_weight,
        "available_carats": diamond.available_carats,
        "color_grade": diamond.color_grade,
        "clarity_grade": diamond.clarity_grade,
        "cut_grade": diamond.cut_grade,
        "polish": diamond.polish,
        "symmetry": diamond.symmetry,
        "fluorescence": diamond.fluorescence,
        "measurements_mm": diamond.measurements_mm,
        "table_pct": diamond.table_pct,
        "depth_pct": diamond.depth_pct,
        "diamond_type": diamond.diamond_type,
        "treatment": diamond.treatment,
        "certificate_lab": diamond.certificate_lab,
        "certificate_number": diamond.certificate_number,
        "certificate_url": diamond.certificate_url,
        "purchase_cost": diamond.purchase_cost,
        "calculated_acquisition_cost": diamond.calculated_acquisition_cost,
        "asking_price": diamond.asking_price,
        "min_selling_price": diamond.min_selling_price,
        "status": diamond.status,
        "location_id": diamond.location_id,
        "supplier_id": diamond.supplier_id,
        "notes": diamond.notes,
        "created_at": diamond.created_at,
        "updated_at": diamond.updated_at,
        "location_name": diamond.location.name if diamond.location else None,
        "supplier_name": diamond.supplier.business_name if diamond.supplier else None,
    }

@router.put("/{diamond_id}")
def edit_diamond(
    diamond_id: str,
    diamond_in: DiamondUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return diamond_service.update_diamond(db, diamond_id, diamond_in, current_user.id)

@router.post("/{diamond_id}/reserve")
def reserve_diamond_item(
    diamond_id: str,
    res_in: DiamondReservationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER, UserRole.SALES_STAFF]))
):
    return diamond_service.reserve_diamond(
        db=db,
        diamond_id=diamond_id,
        customer_id=res_in.customer_id,
        hours=res_in.expires_in_hours or 48,
        user_id=current_user.id,
        notes=res_in.notes
    )

@router.post("/{diamond_id}/release")
def release_diamond_item(
    diamond_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER, UserRole.SALES_STAFF]))
):
    return diamond_service.release_reservation(db, diamond_id, current_user.id)

@router.post("/adjust")
def adjust_diamond_stock(
    adjustment: DiamondAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return diamond_service.adjust_diamond(db, adjustment, current_user.id)
