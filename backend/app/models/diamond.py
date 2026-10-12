from sqlalchemy import Column, String, Boolean, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class Diamond(TimeStampedModel):
    __tablename__ = "diamonds"

    sku = Column(String(64), unique=True, index=True, nullable=False)
    is_parcel = Column(Boolean, default=False, nullable=False)
    lot_number = Column(String(64), nullable=True)
    
    # 4Cs and Specifications
    shape = Column(String(32), default="Round", nullable=False)
    carat_weight = Column(Numeric(10, 4), nullable=False)
    available_carats = Column(Numeric(10, 4), nullable=False)  # For parcels or single stone
    color_grade = Column(String(16), nullable=False)
    clarity_grade = Column(String(16), nullable=False)
    cut_grade = Column(String(16), nullable=True)
    polish = Column(String(16), nullable=True)
    symmetry = Column(String(16), nullable=True)
    fluorescence = Column(String(16), default="None", nullable=True)
    measurements_mm = Column(String(64), nullable=True)
    table_pct = Column(Numeric(5, 2), nullable=True)
    depth_pct = Column(Numeric(5, 2), nullable=True)
    
    # Origin & Treatment
    diamond_type = Column(String(32), default="Natural", nullable=False)  # Natural, Lab_Grown
    treatment = Column(String(64), default="None", nullable=True)
    
    # Certification
    certificate_lab = Column(String(32), default="None", nullable=False)  # GIA, IGI, HRD, SGL, In_House, None
    certificate_number = Column(String(64), index=True, nullable=True)
    certificate_url = Column(String(512), nullable=True)
    
    # Financial Valuation (Exact Decimals)
    purchase_cost = Column(Numeric(14, 2), nullable=False)
    calculated_acquisition_cost = Column(Numeric(14, 2), nullable=False)
    asking_price = Column(Numeric(14, 2), nullable=False)
    min_selling_price = Column(Numeric(14, 2), nullable=True)
    
    # State & Location
    status = Column(String(32), default="AVAILABLE", index=True, nullable=False)  # AVAILABLE, RESERVED, SOLD, MOUNTED, RETURNED, DAMAGED
    location_id = Column(String(36), ForeignKey("inventory_locations.id"), nullable=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True)
    
    notes = Column(Text, nullable=True)

    location = relationship("Location", foreign_keys=[location_id])
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
