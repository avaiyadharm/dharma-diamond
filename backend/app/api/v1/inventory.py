from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.inventory_location import Location
from app.models.stock_movement import StockMovement
from app.core.permissions import UserRole
from app.schemas.inventory_location import LocationCreate, LocationOut
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/inventory", tags=["Inventory & Ledger"])

@router.get("/locations", response_model=List[LocationOut])
def list_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Location).filter(Location.is_active == True).all()

@router.post("/locations", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    loc_in: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    loc = Location(**loc_in.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc

@router.get("/movements", response_model=Dict[str, Any])
def list_stock_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    item_type: Optional[str] = None,
    movement_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(StockMovement)
    if item_type:
        query = query.filter(StockMovement.item_type == item_type)
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)

    total = query.count()
    movements = query.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for m in movements:
        sku = None
        if m.diamond:
            sku = m.diamond.sku
        elif m.jewellery_item:
            sku = m.jewellery_item.sku
        elif m.gemstone_id:
            from app.models.gemstone import Gemstone
            g = db.query(Gemstone).filter(Gemstone.id == m.gemstone_id).first()
            sku = g.sku if g else None

        results.append({
            "id": m.id,
            "movement_number": m.movement_number,
            "item_type": m.item_type,
            "diamond_id": m.diamond_id,
            "jewellery_item_id": m.jewellery_item_id,
            "gemstone_id": m.gemstone_id,
            "movement_type": m.movement_type,
            "qty_before": m.qty_before,
            "qty_change": m.qty_change,
            "qty_after": m.qty_after,
            "carat_change": m.carat_change,
            "weight_change_grams": m.weight_change_grams,
            "source_location_id": m.source_location_id,
            "destination_location_id": m.destination_location_id,
            "reference_doc_type": m.reference_doc_type,
            "reference_doc_id": m.reference_doc_id,
            "reason": m.reason,
            "user_id": m.user_id,
            "user_name": m.user.full_name if m.user else None,
            "item_sku": sku,
            "source_location_name": m.source_location.name if m.source_location else None,
            "destination_location_name": m.destination_location.name if m.destination_location else None,
            "created_at": m.created_at
        })

    return {"items": results, "total": total}
