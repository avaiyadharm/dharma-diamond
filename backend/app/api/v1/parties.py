from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.party import Supplier, Customer
from app.core.permissions import UserRole
from app.schemas.party import (
    SupplierCreate, SupplierUpdate, SupplierOut,
    CustomerCreate, CustomerUpdate, CustomerOut
)
from app.api.deps import get_current_user, require_roles
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/parties", tags=["Suppliers & Customers"])

# --- Suppliers ---
@router.get("/suppliers", response_model=List[SupplierOut])
def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Supplier).order_by(Supplier.business_name.asc()).offset(skip).limit(limit).all()

@router.post("/suppliers", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_in: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    existing = db.query(Supplier).filter(Supplier.business_name == supplier_in.business_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier business name already exists")
    
    supplier = Supplier(**supplier_in.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    log_audit_event(
        db=db,
        table_name="suppliers",
        record_id=supplier.id,
        action="CREATE",
        user_id=current_user.id,
        description=f"Created supplier {supplier.business_name}"
    )
    return supplier

@router.put("/suppliers/{supplier_id}", response_model=SupplierOut)
def update_supplier(
    supplier_id: str,
    supplier_in: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    
    for field, val in supplier_in.model_dump(exclude_unset=True).items():
        setattr(supplier, field, val)
    db.commit()
    db.refresh(supplier)
    return supplier

# --- Customers ---
@router.get("/customers", response_model=List[CustomerOut])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Customer).order_by(Customer.name.asc()).offset(skip).limit(limit).all()

@router.post("/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SALES_STAFF]))
):
    customer = Customer(**customer_in.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)

    log_audit_event(
        db=db,
        table_name="customers",
        record_id=customer.id,
        action="CREATE",
        user_id=current_user.id,
        description=f"Created customer {customer.name}"
    )
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: str,
    customer_in: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SALES_STAFF]))
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    for field, val in customer_in.model_dump(exclude_unset=True).items():
        setattr(customer, field, val)
    db.commit()
    db.refresh(customer)
    return customer
