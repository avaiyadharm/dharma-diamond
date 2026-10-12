from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SalesOrderItemCreate(BaseModel):
    item_type: str = "DIAMOND"  # DIAMOND, JEWELLERY, GEMSTONE
    diamond_id: Optional[str] = None
    jewellery_item_id: Optional[str] = None
    gemstone_id: Optional[str] = None
    sku: str
    description: str
    quantity: int = 1
    unit_price: Decimal = Field(..., max_digits=14, decimal_places=2)
    discount: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)

class SalesOrderItemOut(BaseModel):
    id: str
    sales_order_id: str
    item_type: str
    diamond_id: Optional[str] = None
    jewellery_item_id: Optional[str] = None
    gemstone_id: Optional[str] = None
    sku: str
    description: str
    quantity: int
    unit_price: Decimal
    cost_price: Decimal
    discount: Decimal
    line_total: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SalesOrderCreate(BaseModel):
    customer_id: str
    tax_rate_pct: Decimal = Decimal("3.00")
    discount_amount: Decimal = Decimal("0.00")
    notes: Optional[str] = None
    payment_method: Optional[str] = "Bank Transfer"
    initial_payment_amount: Optional[Decimal] = Decimal("0.00")
    items: List[SalesOrderItemCreate]

class SalesOrderOut(BaseModel):
    id: str
    so_number: str
    customer_id: str
    customer_name: Optional[str] = None
    sales_date: datetime
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    payment_status: str
    status: str
    notes: Optional[str] = None
    created_by_user_id: str
    salesperson_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[SalesOrderItemOut] = []

    model_config = ConfigDict(from_attributes=True)

class ItemReservationCreate(BaseModel):
    item_type: str  # DIAMOND, JEWELLERY, GEMSTONE
    diamond_id: Optional[str] = None
    jewellery_item_id: Optional[str] = None
    gemstone_id: Optional[str] = None
    customer_id: str
    expires_in_hours: int = 48
    notes: Optional[str] = None

class ItemReservationOut(BaseModel):
    id: str
    item_type: str
    diamond_id: Optional[str] = None
    jewellery_item_id: Optional[str] = None
    gemstone_id: Optional[str] = None
    customer_id: str
    customer_name: Optional[str] = None
    reserved_by_user_id: str
    reserved_by_name: Optional[str] = None
    reserved_at: datetime
    expires_at: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    item_sku: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
