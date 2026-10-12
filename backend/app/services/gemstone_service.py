from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status

from app.models.gemstone import Gemstone
from app.schemas.gemstone import GemstoneCreate, GemstoneUpdate
from app.services.stock_movement_service import record_movement
from app.services.audit_service import log_audit_event

def get_gemstones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    gemstone_type: Optional[str] = None,
    shape: Optional[str] = None,
    status: Optional[str] = None,
    location_id: Optional[str] = None,
    query: Optional[str] = None
) -> Dict[str, Any]:
    filters = []
    if gemstone_type:
        filters.append(Gemstone.gemstone_type == gemstone_type)
    if shape:
        filters.append(Gemstone.shape == shape)
    if status:
        filters.append(Gemstone.status == status)
    if location_id:
        filters.append(Gemstone.location_id == location_id)
    if query:
        q = f"%{query.strip()}%"
        filters.append(
            or_(
                Gemstone.sku.ilike(q),
                Gemstone.gemstone_type.ilike(q),
                Gemstone.variety.ilike(q),
                Gemstone.certificate_number.ilike(q),
                Gemstone.notes.ilike(q)
            )
        )

    base_query = db.query(Gemstone)
    if filters:
        base_query = base_query.filter(and_(*filters))

    total = base_query.count()
    items = base_query.order_by(Gemstone.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for it in items:
        results.append({
            "id": it.id,
            "sku": it.sku,
            "gemstone_type": it.gemstone_type,
            "variety": it.variety,
            "is_natural": it.is_natural,
            "carat_weight": it.carat_weight,
            "shape": it.shape,
            "color": it.color,
            "clarity": it.clarity,
            "cut": it.cut,
            "treatment": it.treatment,
            "certificate_lab": it.certificate_lab,
            "certificate_number": it.certificate_number,
            "purchase_cost": it.purchase_cost,
            "selling_price": it.selling_price,
            "status": it.status,
            "location_id": it.location_id,
            "supplier_id": it.supplier_id,
            "notes": it.notes,
            "created_at": it.created_at,
            "updated_at": it.updated_at,
            "location_name": it.location.name if it.location else None,
            "supplier_name": it.supplier.business_name if it.supplier else None
        })

    return {"items": results, "total": total}

def create_gemstone(db: Session, gem_in: GemstoneCreate, user_id: str) -> Gemstone:
    existing = db.query(Gemstone).filter(Gemstone.sku == gem_in.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gemstone with SKU '{gem_in.sku}' already exists"
        )

    gem = Gemstone(**gem_in.model_dump())
    db.add(gem)
    db.flush()

    record_movement(
        db=db,
        item_type="GEMSTONE",
        gemstone_id=gem.id,
        movement_type="OPENING_STOCK",
        user_id=user_id,
        qty_before=0,
        qty_change=1,
        qty_after=1,
        carat_change=gem.carat_weight,
        destination_location_id=gem.location_id,
        reason=f"Registered gemstone: {gem.sku} ({gem.gemstone_type})"
    )

    log_audit_event(
        db=db,
        table_name="gemstones",
        record_id=gem.id,
        action="CREATE",
        user_id=user_id,
        description=f"Created gemstone {gem.sku} ({gem.carat_weight}ct {gem.gemstone_type})"
    )

    db.commit()
    db.refresh(gem)
    return gem

def update_gemstone(db: Session, gem_id: str, gem_in: GemstoneUpdate, user_id: str) -> Gemstone:
    gem = db.query(Gemstone).filter(Gemstone.id == gem_id).first()
    if not gem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gemstone not found")

    update_data = gem_in.model_dump(exclude_unset=True)

    if "location_id" in update_data and update_data["location_id"] != gem.location_id:
        record_movement(
            db=db,
            item_type="GEMSTONE",
            gemstone_id=gem.id,
            movement_type="LOCATION_TRANSFER",
            user_id=user_id,
            qty_before=1,
            qty_change=0,
            qty_after=1,
            source_location_id=gem.location_id,
            destination_location_id=update_data["location_id"],
            reason="Location transfer"
        )

    for field, val in update_data.items():
        setattr(gem, field, val)

    log_audit_event(
        db=db,
        table_name="gemstones",
        record_id=gem.id,
        action="UPDATE",
        user_id=user_id,
        description=f"Updated gemstone {gem.sku}"
    )

    db.commit()
    db.refresh(gem)
    return gem
