from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime

class InvoiceOut(BaseModel):
    id: str
    invoice_number: str
    invoice_date: datetime
    sales_order_id: str
    customer_id: str
    customer_name: Optional[str] = None
    subtotal: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    total_tax: Decimal
    discount_amount: Decimal
    grand_total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    status: str
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    payment_type: str = "CUSTOMER_PAYMENT"  # CUSTOMER_PAYMENT, SUPPLIER_PAYMENT, REFUND
    invoice_id: Optional[str] = None
    purchase_order_id: Optional[str] = None
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    amount: Decimal = Field(..., max_digits=14, decimal_places=2, gt=0)
    payment_method: str = "Bank Transfer"  # Bank Transfer, UPI, Cash, Card, Cheque
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentOut(BaseModel):
    id: str
    payment_number: str
    payment_date: datetime
    payment_type: str
    invoice_id: Optional[str] = None
    invoice_number: Optional[str] = None
    purchase_order_id: Optional[str] = None
    po_number: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    amount: Decimal
    payment_method: str
    reference_number: Optional[str] = None
    recorded_by_user_id: str
    recorder_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
