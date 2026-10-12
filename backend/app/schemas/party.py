from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- Supplier Schemas ---
class SupplierBase(BaseModel):
    business_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    country: str = "India"
    currency: str = "INR"
    payment_terms: Optional[str] = "Net 30 Days"
    category: str = "Rough & Polished Diamonds"
    notes: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class SupplierOut(SupplierBase):
    id: str
    created_at: datetime
    updated_at: datetime
    total_purchases: Optional[Decimal] = Decimal("0.00")
    total_paid: Optional[Decimal] = Decimal("0.00")
    outstanding_balance: Optional[Decimal] = Decimal("0.00")

    class Config:
        from_attributes = True

# --- Customer Schemas ---
class CustomerBase(BaseModel):
    name: str
    company_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    tax_id: Optional[str] = None
    customer_type: str = "Retail"  # Retail, Wholesale
    notes: Optional[str] = None
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    tax_id: Optional[str] = None
    customer_type: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class CustomerOut(CustomerBase):
    id: str
    created_at: datetime
    updated_at: datetime
    total_purchases: Optional[Decimal] = Decimal("0.00")
    total_paid: Optional[Decimal] = Decimal("0.00")
    outstanding_balance: Optional[Decimal] = Decimal("0.00")

    class Config:
        from_attributes = True
