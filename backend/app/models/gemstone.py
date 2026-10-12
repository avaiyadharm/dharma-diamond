from sqlalchemy import Column, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class Gemstone(TimeStampedModel):
    __tablename__ = "gemstones"

    sku = Column(String(64), unique=True, index=True, nullable=False)
    gemstone_type = Column(String(64), nullable=False)  # Ruby, Emerald, Blue Sapphire, Yellow Sapphire, Tanzanite, Pearl, Other
    variety = Column(String(64), nullable=True)         # Burmese Ruby, Zambian Emerald, Ceylon Sapphire
    is_natural = Column(Boolean, default=True, nullable=False)
    carat_weight = Column(Numeric(10, 4), nullable=False)
    shape = Column(String(32), default="Oval", nullable=False)
    color = Column(String(32), nullable=False)
    clarity = Column(String(32), nullable=True)
    cut = Column(String(32), nullable=True)
    treatment = Column(String(64), default="None", nullable=True)
    certificate_lab = Column(String(32), default="None", nullable=False)
    certificate_number = Column(String(64), nullable=True)
    purchase_cost = Column(Numeric(14, 2), nullable=False)
    selling_price = Column(Numeric(14, 2), nullable=False)
    status = Column(String(32), default="AVAILABLE", index=True, nullable=False)
    location_id = Column(String(36), ForeignKey("inventory_locations.id"), nullable=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True)
    notes = Column(Text, nullable=True)

    location = relationship("Location", foreign_keys=[location_id])
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
