from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import UserRole
from app.schemas.invoice_payment import PaymentCreate, PaymentOut
from app.api.deps import get_current_user, require_roles
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("", response_model=Dict[str, Any])
def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    payment_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return payment_service.get_payments(
        db=db,
        skip=skip,
        limit=limit,
        payment_type=payment_type,
        customer_id=customer_id,
        supplier_id=supplier_id
    )

@router.post("", status_code=status.HTTP_201_CREATED)
def record_payment_entry(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.SALES_STAFF]))
):
    return payment_service.record_payment(db, payment_in, current_user.id)
