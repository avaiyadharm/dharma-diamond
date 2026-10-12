from sqlalchemy import Column, String, Numeric, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class JewelleryProduct(TimeStampedModel):
    __tablename__ = "jewellery_products"

    design_code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(190), nullable=False)
    category = Column(String(64), nullable=False)  # Ring, Necklace, Pendant, Earrings, Bracelet, Bangles, Chain, Other
    collection = Column(String(128), nullable=True)
    metal_type = Column(String(32), default="Gold", nullable=False)  # Gold, Platinum, Silver, Other
    purity = Column(String(32), default="18K", nullable=False)       # 14K, 18K, 22K, 24K, 950 Pt
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)

    items = relationship("JewelleryItem", back_populates="product", cascade="all, delete-orphan")

class JewelleryItem(TimeStampedModel):
    __tablename__ = "jewellery_items"

    sku = Column(String(64), unique=True, index=True, nullable=False)
    product_id = Column(String(36), ForeignKey("jewellery_products.id"), nullable=False)
    
    # Weight Specifications (Never conflated)
    gross_weight_grams = Column(Numeric(10, 4), nullable=False)
    net_metal_weight_grams = Column(Numeric(10, 4), nullable=False)
    total_stone_carats = Column(Numeric(10, 4), default=0, nullable=False)
    hallmark_details = Column(String(64), nullable=True)
    
    # Cost Breakdown & Valuation (Exact Decimals)
    metal_cost = Column(Numeric(14, 2), default=0, nullable=False)
    stone_cost = Column(Numeric(14, 2), default=0, nullable=False)
    making_charge = Column(Numeric(14, 2), default=0, nullable=False)
    other_costs = Column(Numeric(14, 2), default=0, nullable=False)
    total_cost = Column(Numeric(14, 2), nullable=False)
    selling_price = Column(Numeric(14, 2), nullable=False)
    
    status = Column(String(32), default="AVAILABLE", index=True, nullable=False)  # AVAILABLE, RESERVED, SOLD, DISMANTLED, DAMAGED
    location_id = Column(String(36), ForeignKey("inventory_locations.id"), nullable=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True)
    image_url = Column(String(512), nullable=True)
    notes = Column(Text, nullable=True)

    product = relationship("JewelleryProduct", back_populates="items")
    location = relationship("Location", foreign_keys=[location_id])
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
    stones = relationship("JewelleryStone", back_populates="jewellery_item", cascade="all, delete-orphan")

class JewelleryStone(TimeStampedModel):
    __tablename__ = "jewellery_stones"

    jewellery_item_id = Column(String(36), ForeignKey("jewellery_items.id"), nullable=False)
    diamond_id = Column(String(36), ForeignKey("diamonds.id"), nullable=True)
    
    stone_type = Column(String(32), default="Diamond", nullable=False)  # Diamond, Ruby, Sapphire, Emerald, Gemstone
    stone_count = Column(Integer, default=1, nullable=False)
    carat_weight = Column(Numeric(10, 4), nullable=False)
    shape = Column(String(32), default="Round", nullable=True)
    color = Column(String(32), nullable=True)
    clarity = Column(String(32), nullable=True)
    setting_type = Column(String(32), default="Prong", nullable=True)  # Prong, Bezel, Pave, Channel, Tension

    jewellery_item = relationship("JewelleryItem", back_populates="stones")
    diamond = relationship("Diamond", foreign_keys=[diamond_id])
