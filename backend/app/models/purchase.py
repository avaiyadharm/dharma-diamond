from sqlalchemy import Column, String, Numeric, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import TimeStampedModel

class PurchaseOrder(TimeStampedModel):
    __tablename__ = "purchase_orders"

    po_number = Column(String(64), unique=True, index=True, nullable=False)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=False)
    purchase_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expected_delivery_date = Column(DateTime, nullable=True)
    
    subtotal = Column(Numeric(14, 2), default=0, nullable=False)
    tax_amount = Column(Numeric(14, 2), default=0, nullable=False)
    total_amount = Column(Numeric(14, 2), default=0, nullable=False)
    amount_paid = Column(Numeric(14, 2), default=0, nullable=False)
    
    payment_status = Column(String(32), default="UNPAID", nullable=False)  # UNPAID, PARTIALLY_PAID, PAID
    status = Column(String(32), default="CONFIRMED", index=True, nullable=False)  # DRAFT, CONFIRMED, PARTIALLY_RECEIVED, RECEIVED, CANCELLED
    notes = Column(Text, nullable=True)

    supplier = relationship("Supplier", foreign_keys=[supplier_id])
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    receipts = relationship("GoodsReceipt", back_populates="purchase_order")

class PurchaseOrderItem(TimeStampedModel):
    __tablename__ = "purchase_order_items"

    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=False)
    item_type = Column(String(32), default="DIAMOND", nullable=False)  # DIAMOND, JEWELLERY, GEMSTONE
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    carat_weight = Column(Numeric(10, 4), nullable=True)
    unit_price = Column(Numeric(14, 2), nullable=False)
    line_total = Column(Numeric(14, 2), nullable=False)
    received_quantity = Column(Integer, default=0, nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")

class GoodsReceipt(TimeStampedModel):
    __tablename__ = "goods_receipts"

    receipt_number = Column(String(64), unique=True, index=True, nullable=False)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=False)
    received_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    received_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)

    purchase_order = relationship("PurchaseOrder", back_populates="receipts")
    receiver = relationship("User", foreign_keys=[received_by_user_id])
