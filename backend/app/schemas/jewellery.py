from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime

# --- Stone Schemas ---
class JewelleryStoneBase(BaseModel):
    stone_type: str = "Diamond"  # Diamond, Ruby, Sapphire, Emerald, Gemstone
    diamond_id: Optional[str] = None
    stone_count: int = 1
    carat_weight: Decimal = Field(..., max_digits=10, decimal_places=4)
    shape: Optional[str] = "Round"
    color: Optional[str] = None
    clarity: Optional[str] = None
    setting_type: Optional[str] = "Prong"  # Prong, Bezel, Pave, Channel, Tension

class JewelleryStoneCreate(JewelleryStoneBase):
    pass

class JewelleryStoneOut(JewelleryStoneBase):
    id: str
    jewellery_item_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Master Design Product Schemas ---
class JewelleryProductBase(BaseModel):
    design_code: str
    name: str
    category: str  # Ring, Necklace, Pendant, Earrings, Bracelet, Bangles, Chain, Other
    collection: Optional[str] = None
    metal_type: str = "Gold"  # Gold, Platinum, Silver, Other
    purity: str = "18K"       # 14K, 18K, 22K, 24K, 950 Pt
    description: Optional[str] = None
    image_url: Optional[str] = None

class JewelleryProductCreate(JewelleryProductBase):
    pass

class JewelleryProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    collection: Optional[str] = None
    metal_type: Optional[str] = None
    purity: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class JewelleryProductOut(JewelleryProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    item_count: Optional[int] = 0

    class Config:
        from_attributes = True

# --- Serialized Physical Jewellery Item Schemas ---
class JewelleryItemBase(BaseModel):
    sku: str
    product_id: str
    gross_weight_grams: Decimal = Field(..., max_digits=10, decimal_places=4)
    net_metal_weight_grams: Decimal = Field(..., max_digits=10, decimal_places=4)
    total_stone_carats: Decimal = Field(default=Decimal("0.0000"), max_digits=10, decimal_places=4)
    hallmark_details: Optional[str] = "BIS 750 (18K)"
    
    metal_cost: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    stone_cost: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    making_charge: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    other_costs: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    total_cost: Decimal = Field(..., max_digits=14, decimal_places=2)
    selling_price: Decimal = Field(..., max_digits=14, decimal_places=2)
    
    status: str = "AVAILABLE"  # AVAILABLE, RESERVED, SOLD, DISMANTLED, DAMAGED
    location_id: Optional[str] = None
    supplier_id: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None

class JewelleryItemCreate(JewelleryItemBase):
    stones: Optional[List[JewelleryStoneCreate]] = []

class JewelleryItemUpdate(BaseModel):
    gross_weight_grams: Optional[Decimal] = None
    net_metal_weight_grams: Optional[Decimal] = None
    total_stone_carats: Optional[Decimal] = None
    hallmark_details: Optional[str] = None
    metal_cost: Optional[Decimal] = None
    stone_cost: Optional[Decimal] = None
    making_charge: Optional[Decimal] = None
    other_costs: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    status: Optional[str] = None
    location_id: Optional[str] = None
    supplier_id: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None

class JewelleryItemOut(JewelleryItemBase):
    id: str
    created_at: datetime
    updated_at: datetime
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    design_code: Optional[str] = None
    metal_type: Optional[str] = None
    purity: Optional[str] = None
    location_name: Optional[str] = None
    supplier_name: Optional[str] = None
    stones: List[JewelleryStoneOut] = []

    class Config:
        from_attributes = True
