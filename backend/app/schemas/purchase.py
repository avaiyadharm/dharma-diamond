from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime

class PurchaseOrderItemBase(BaseModel):
    item_type: str = "DIAMOND"  # DIAMOND, JEWELLERY, GEMSTONE
    description: str
    quantity: int = 1
    carat_weight: Optional[Decimal] = None
    unit_price: Decimal = Field(..., max_digits=14, decimal_places=2)
    line_total: Decimal = Field(..., max_digits=14, decimal_places=2)

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemOut(PurchaseOrderItemBase):
    id: str
    purchase_order_id: str
    received_quantity: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PurchaseOrderBase(BaseModel):
    supplier_id: str
    expected_delivery_date: Optional[datetime] = None
    subtotal: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    total_amount: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    notes: Optional[str] = None

class PurchaseOrderCreate(BaseModel):
    supplier_id: str
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    tax_rate_pct: Decimal = Decimal("3.00")
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderUpdate(BaseModel):
    expected_delivery_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class GoodsReceiptCreate(BaseModel):
    purchase_order_id: str
    notes: Optional[str] = None
    # For receiving serialized diamonds or items into a location
    location_id: Optional[str] = None

class GoodsReceiptOut(BaseModel):
    id: str
    receipt_number: str
    purchase_order_id: str
    received_date: datetime
    received_by_user_id: str
    receiver_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PurchaseOrderOut(PurchaseOrderBase):
    id: str
    po_number: str
    purchase_date: datetime
    amount_paid: Decimal
    payment_status: str
    status: str
    supplier_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseOrderItemOut] = []
    receipts: List[GoodsReceiptOut] = []

    class Config:
        from_attributes = True
