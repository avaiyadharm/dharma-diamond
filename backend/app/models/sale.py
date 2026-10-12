from sqlalchemy import Column, String, Numeric, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import TimeStampedModel

class SalesOrder(TimeStampedModel):
    __tablename__ = "sales_orders"

    so_number = Column(String(64), unique=True, index=True, nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    sales_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    subtotal = Column(Numeric(14, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(14, 2), default=0, nullable=False)
    tax_amount = Column(Numeric(14, 2), default=0, nullable=False)
    total_amount = Column(Numeric(14, 2), default=0, nullable=False)
    amount_paid = Column(Numeric(14, 2), default=0, nullable=False)
    
    payment_status = Column(String(32), default="UNPAID", nullable=False)  # UNPAID, PARTIALLY_PAID, PAID
    status = Column(String(32), default="CONFIRMED", index=True, nullable=False)  # DRAFT, CONFIRMED, DELIVERED, CANCELLED, RETURNED
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", foreign_keys=[customer_id])
    salesperson = relationship("User", foreign_keys=[created_by_user_id])
    items = relationship("SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="sales_order")

class SalesOrderItem(TimeStampedModel):
    __tablename__ = "sales_order_items"

    sales_order_id = Column(String(36), ForeignKey("sales_orders.id"), nullable=False)
    item_type = Column(String(32), default="DIAMOND", nullable=False)  # DIAMOND, JEWELLERY, GEMSTONE
    diamond_id = Column(String(36), ForeignKey("diamonds.id"), nullable=True)
    jewellery_item_id = Column(String(36), ForeignKey("jewellery_items.id"), nullable=True)
    gemstone_id = Column(String(36), ForeignKey("gemstones.id"), nullable=True)
    
    sku = Column(String(64), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(14, 2), nullable=False)
    cost_price = Column(Numeric(14, 2), default=0, nullable=False)  # Snapshot for COGS / Gross profit calculation
    discount = Column(Numeric(14, 2), default=0, nullable=False)
    line_total = Column(Numeric(14, 2), nullable=False)

    sales_order = relationship("SalesOrder", back_populates="items")
    diamond = relationship("Diamond", foreign_keys=[diamond_id])
    jewellery_item = relationship("JewelleryItem", foreign_keys=[jewellery_item_id])

class ItemReservation(TimeStampedModel):
    __tablename__ = "item_reservations"

    item_type = Column(String(32), nullable=False)  # DIAMOND, JEWELLERY, GEMSTONE
    diamond_id = Column(String(36), ForeignKey("diamonds.id"), nullable=True)
    jewellery_item_id = Column(String(36), ForeignKey("jewellery_items.id"), nullable=True)
    gemstone_id = Column(String(36), ForeignKey("gemstones.id"), nullable=True)
    
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    reserved_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    reserved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String(32), default="ACTIVE", nullable=False)  # ACTIVE, EXPIRED, CONVERTED_TO_SALE, RELEASED
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", foreign_keys=[customer_id])
    user = relationship("User", foreign_keys=[reserved_by_user_id])
