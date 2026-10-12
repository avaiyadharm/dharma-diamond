from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

class StockMovementBase(BaseModel):
    item_type: str  # DIAMOND, JEWELLERY, GEMSTONE
    diamond_id: Optional[str] = None
    jewellery_item_id: Optional[str] = None
    gemstone_id: Optional[str] = None
    
    movement_type: str  # OPENING_STOCK, PURCHASE_RECEIPT, SALE, CUSTOMER_RETURN, SUPPLIER_RETURN, LOCATION_TRANSFER, STOCK_ADJUSTMENT, MOUNTED_IN_JEWELLERY, DISMANTLED
    qty_before: int = 0
    qty_change: int
    qty_after: int = 0
    
    carat_change: Optional[Decimal] = None
    weight_change_grams: Optional[Decimal] = None
    
    source_location_id: Optional[str] = None
    destination_location_id: Optional[str] = None
    
    reference_doc_type: Optional[str] = None
    reference_doc_id: Optional[str] = None
    reason: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovementOut(StockMovementBase):
    id: str
    movement_number: str
    created_at: datetime
    user_id: str
    user_name: Optional[str] = None
    item_sku: Optional[str] = None
    source_location_name: Optional[str] = None
    destination_location_name: Optional[str] = None

    class Config:
        from_attributes = True
