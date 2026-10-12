from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import UserRole
from app.schemas.purchase import PurchaseOrderCreate, GoodsReceiptCreate
from app.api.deps import get_current_user, require_roles
from app.services import purchase_service

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.get("", response_model=Dict[str, Any])
def list_purchases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    supplier_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return purchase_service.get_purchase_orders(
        db=db,
        skip=skip,
        limit=limit,
        supplier_id=supplier_id,
        status_filter=status_filter
    )

@router.post("", status_code=status.HTTP_201_CREATED)
def create_purchase(
    po_in: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return purchase_service.create_purchase_order(db, po_in, current_user.id)

@router.post("/receive", status_code=status.HTTP_201_CREATED)
def receive_goods_intake(
    receipt_in: GoodsReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return purchase_service.receive_goods(db, receipt_in, current_user.id)
