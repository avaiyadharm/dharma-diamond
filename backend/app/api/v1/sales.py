from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import UserRole
from app.schemas.sale import SalesOrderCreate, SalesOrderOut
from app.api.deps import get_current_user, require_roles
from app.services import sale_service

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.get("", response_model=Dict[str, Any])
def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return sale_service.get_sales_orders(
        db=db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        status_filter=status_filter
    )

@router.post("", response_model=SalesOrderOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    so_in: SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SALES_STAFF]))
):
    return sale_service.create_sales_order(db, so_in, current_user.id)

@router.post("/{sales_order_id}/cancel")
def cancel_sale(
    sales_order_id: str,
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    return sale_service.cancel_sales_order(db, sales_order_id, reason, current_user.id)
