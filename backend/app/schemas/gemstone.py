from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime

class GemstoneBase(BaseModel):
    sku: str
    gemstone_type: str  # Ruby, Emerald, Blue Sapphire, Yellow Sapphire, Tanzanite, Pearl, Other
    variety: Optional[str] = None
    is_natural: bool = True
    carat_weight: Decimal = Field(..., max_digits=10, decimal_places=4)
    shape: str = "Oval"
    color: str
    clarity: Optional[str] = None
    cut: Optional[str] = None
    treatment: Optional[str] = "None"
    certificate_lab: str = "None"
    certificate_number: Optional[str] = None
    purchase_cost: Decimal = Field(..., max_digits=14, decimal_places=2)
    selling_price: Decimal = Field(..., max_digits=14, decimal_places=2)
    status: str = "AVAILABLE"
    location_id: Optional[str] = None
    supplier_id: Optional[str] = None
    notes: Optional[str] = None

class GemstoneCreate(GemstoneBase):
    pass

class GemstoneUpdate(BaseModel):
    gemstone_type: Optional[str] = None
    variety: Optional[str] = None
    is_natural: Optional[bool] = None
    carat_weight: Optional[Decimal] = None
    shape: Optional[str] = None
    color: Optional[str] = None
    clarity: Optional[str] = None
    cut: Optional[str] = None
    treatment: Optional[str] = None
    certificate_lab: Optional[str] = None
    certificate_number: Optional[str] = None
    purchase_cost: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    status: Optional[str] = None
    location_id: Optional[str] = None
    supplier_id: Optional[str] = None
    notes: Optional[str] = None

class GemstoneOut(GemstoneBase):
    id: str
    created_at: datetime
    updated_at: datetime
    location_name: Optional[str] = None
    supplier_name: Optional[str] = None

    class Config:
        from_attributes = True
