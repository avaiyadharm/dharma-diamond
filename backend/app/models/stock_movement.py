from sqlalchemy import Column, String, Numeric, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import TimeStampedModel

class StockMovement(TimeStampedModel):
    __tablename__ = "stock_movements"

    movement_number = Column(String(64), unique=True, index=True, nullable=False)
    item_type = Column(String(32), nullable=False)  # DIAMOND, JEWELLERY, GEMSTONE
    
    diamond_id = Column(String(36), ForeignKey("diamonds.id"), nullable=True)
    jewellery_item_id = Column(String(36), ForeignKey("jewellery_items.id"), nullable=True)
    gemstone_id = Column(String(36), ForeignKey("gemstones.id"), nullable=True)
    
    movement_type = Column(String(32), index=True, nullable=False)  
    # OPENING_STOCK, PURCHASE_RECEIPT, SALE, CUSTOMER_RETURN, SUPPLIER_RETURN, LOCATION_TRANSFER, STOCK_ADJUSTMENT, MOUNTED_IN_JEWELLERY, DISMANTLED
    
    qty_before = Column(Integer, default=0, nullable=False)
    qty_change = Column(Integer, nullable=False)
    qty_after = Column(Integer, default=0, nullable=False)
    
    carat_change = Column(Numeric(10, 4), nullable=True)
    weight_change_grams = Column(Numeric(10, 4), nullable=True)
    
    source_location_id = Column(String(36), ForeignKey("inventory_locations.id"), nullable=True)
    destination_location_id = Column(String(36), ForeignKey("inventory_locations.id"), nullable=True)
    
    reference_doc_type = Column(String(32), nullable=True)  # PURCHASE, SALE, RETURN, MANUAL_ADJUSTMENT
    reference_doc_id = Column(String(64), nullable=True)
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)

    diamond = relationship("Diamond", foreign_keys=[diamond_id])
    jewellery_item = relationship("JewelleryItem", foreign_keys=[jewellery_item_id])
    source_location = relationship("Location", foreign_keys=[source_location_id])
    destination_location = relationship("Location", foreign_keys=[destination_location_id])
    user = relationship("User", foreign_keys=[user_id])
