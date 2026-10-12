from sqlalchemy import Column, String, Boolean, Text
from app.models.base import TimeStampedModel

class Supplier(TimeStampedModel):
    __tablename__ = "suppliers"

    business_name = Column(String(190), unique=True, index=True, nullable=False)
    contact_person = Column(String(128), nullable=True)
    phone = Column(String(32), nullable=True)
    email = Column(String(128), nullable=True)
    address = Column(Text, nullable=True)
    tax_id = Column(String(64), nullable=True)  # GSTIN or TIN
    country = Column(String(64), default="India", nullable=False)
    currency = Column(String(8), default="INR", nullable=False)
    payment_terms = Column(String(128), nullable=True)
    category = Column(String(64), default="Rough & Polished Diamonds", nullable=False)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

class Customer(TimeStampedModel):
    __tablename__ = "customers"

    name = Column(String(190), index=True, nullable=False)
    company_name = Column(String(190), nullable=True)
    phone = Column(String(32), index=True, nullable=True)
    email = Column(String(128), index=True, nullable=True)
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    tax_id = Column(String(64), nullable=True)  # GSTIN or PAN
    customer_type = Column(String(32), default="Retail", nullable=False)  # Retail, Wholesale
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
