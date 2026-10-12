from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import TimeStampedModel

class Invoice(TimeStampedModel):
    __tablename__ = "invoices"

    invoice_number = Column(String(64), unique=True, index=True, nullable=False)
    invoice_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    sales_order_id = Column(String(36), ForeignKey("sales_orders.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    
    subtotal = Column(Numeric(14, 2), default=0, nullable=False)
    cgst_rate = Column(Numeric(5, 2), default=1.5, nullable=False)
    cgst_amount = Column(Numeric(14, 2), default=0, nullable=False)
    sgst_rate = Column(Numeric(5, 2), default=1.5, nullable=False)
    sgst_amount = Column(Numeric(14, 2), default=0, nullable=False)
    igst_rate = Column(Numeric(5, 2), default=0.0, nullable=False)
    igst_amount = Column(Numeric(14, 2), default=0, nullable=False)
    total_tax = Column(Numeric(14, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(14, 2), default=0, nullable=False)
    grand_total = Column(Numeric(14, 2), default=0, nullable=False)
    amount_paid = Column(Numeric(14, 2), default=0, nullable=False)
    balance_due = Column(Numeric(14, 2), default=0, nullable=False)
    
    status = Column(String(32), default="ISSUED", nullable=False)  # ISSUED, PAID, PARTIALLY_PAID, CANCELLED
    payment_terms = Column(String(128), default="Due on Receipt", nullable=True)
    notes = Column(Text, nullable=True)

    sales_order = relationship("SalesOrder", back_populates="invoices")
    customer = relationship("Customer", foreign_keys=[customer_id])
    payments = relationship("Payment", back_populates="invoice")

class Payment(TimeStampedModel):
    __tablename__ = "payments"

    payment_number = Column(String(64), unique=True, index=True, nullable=False)
    payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    payment_type = Column(String(32), default="CUSTOMER_PAYMENT", nullable=False)  # CUSTOMER_PAYMENT, SUPPLIER_PAYMENT, REFUND
    
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=True)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True)
    
    amount = Column(Numeric(14, 2), nullable=False)
    payment_method = Column(String(32), default="Bank Transfer", nullable=False)  # Bank Transfer, UPI, Cash, Card, Cheque
    reference_number = Column(String(128), nullable=True)
    recorded_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", foreign_keys=[customer_id])
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
    user = relationship("User", foreign_keys=[recorded_by_user_id])
