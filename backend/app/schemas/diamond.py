from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime

class DiamondBase(BaseModel):
    sku: str
    is_parcel: bool = False
    lot_number: Optional[str] = None
    
    # 4Cs & Specifications
    shape: str = "Round"
    carat_weight: Decimal = Field(..., max_digits=10, decimal_places=4)
    available_carats: Optional[Decimal] = None
    color_grade: str
    clarity_grade: str
    cut_grade: Optional[str] = "Excellent"
    polish: Optional[str] = "Excellent"
    symmetry: Optional[str] = "Excellent"
    fluorescence: Optional[str] = "None"
    measurements_mm: Optional[str] = None
    table_pct: Optional[Decimal] = None
    depth_pct: Optional[Decimal] = None
    
    # Origin & Treatment
    diamond_type: str = "Natural"  # Natural, Lab_Grown
    treatment: Optional[str] = "None"
    
    # Certification
    certificate_lab: str = "None"  # GIA, IGI, HRD, SGL, In_House, None
    certificate_number: Optional[str] = None
    certificate_url: Optional[str] = None
    
    # Financial Valuation (Exact Decimals)
    purchase_cost: Decimal = Field(..., max_digits=14, decimal_places=2)
    calculated_acquisition_cost: Optional[Decimal] = None
    asking_price: Decimal = Field(..., max_digits=14, decimal_places=2)
    min_selling_price: Optional[Decimal] = None
    
    # State & Location
    status: str = "AVAILABLE"  # AVAILABLE, RESERVED, SOLD, MOUNTED, RETURNED, DAMAGED
    location_id: Optional[str] = None
    supplier_id: Optional[str] = None
    notes: Optional[str] = None

class DiamondCreate(DiamondBase):
    pass

class DiamondUpdate(BaseModel):
    lot_number: Optional[str] = None
    shape: Optional[str] = None
    carat_weight: Optional[Decimal] = None
    available_carats: Optional[Decimal] = None
    color_grade: Optional[str] = None
    clarity_grade: Optional[str] = None
    cut_grade: Optional[str] = None
    polish: Optional[str] = None
    symmetry: Optional[str] = None
    fluorescence: Optional[str] = None
    measurements_mm: Optional[str] = None
    table_pct: Optional[Decimal] = None
    depth_pct: Optional[Decimal] = None
    diamond_type: Optional[str] = None
    treatment: Optional[str] = None
    certificate_lab: Optional[str] = None
    certificate_number: Optional[str] = None
    certificate_url: Optional[str] = None
    purchase_cost: Optional[Decimal] = None
    calculated_acquisition_cost: Optional[Decimal] = None
    asking_price: Optional[Decimal] = None
    min_selling_price: Optional[Decimal] = None
    status: Optional[str] = None
    location_id: Optional[str] = None
    supplier_id: Optional[str] = None
    notes: Optional[str] = None

class DiamondOut(DiamondBase):
    id: str
    created_at: datetime
    updated_at: datetime
    location_name: Optional[str] = None
    supplier_name: Optional[str] = None

    class Config:
        from_attributes = True

class DiamondAdjustment(BaseModel):
    diamond_id: str
    adjustment_type: str  # DAMAGE, CARAT_REDUCTION, REVALUATION, LOCATION_TRANSFER
    new_status: Optional[str] = None
    new_location_id: Optional[str] = None
    carat_change: Optional[Decimal] = Decimal("0.0000")
    reason: str

class DiamondReservationRequest(BaseModel):
    customer_id: str
    expires_in_hours: Optional[int] = 48
    notes: Optional[str] = None
