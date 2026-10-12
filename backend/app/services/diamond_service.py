from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status

from app.models.diamond import Diamond
from app.models.inventory_location import Location
from app.models.party import Supplier, Customer
from app.models.sale import ItemReservation
from app.core.inventory import InventoryState, validate_inventory_transition
from app.schemas.diamond import DiamondCreate, DiamondUpdate, DiamondAdjustment
from app.services.stock_movement_service import record_movement
from app.services.audit_service import log_audit_event

def get_diamonds(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    shape: Optional[str] = None,
    color_grade: Optional[str] = None,
    clarity_grade: Optional[str] = None,
    min_carat: Optional[Decimal] = None,
    max_carat: Optional[Decimal] = None,
    status: Optional[str] = None,
    location_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    diamond_type: Optional[str] = None
) -> Dict[str, Any]:
    filters = []
    
    if query:
        q = f"%{query.strip()}%"
        filters.append(
            or_(
                Diamond.sku.ilike(q),
                Diamond.certificate_number.ilike(q),
                Diamond.lot_number.ilike(q),
                Diamond.notes.ilike(q)
            )
        )
    if shape:
        filters.append(Diamond.shape == shape)
    if color_grade:
        filters.append(Diamond.color_grade == color_grade)
    if clarity_grade:
        filters.append(Diamond.clarity_grade == clarity_grade)
    if min_carat is not None:
        filters.append(Diamond.carat_weight >= min_carat)
    if max_carat is not None:
        filters.append(Diamond.carat_weight <= max_carat)
    if status:
        filters.append(Diamond.status == status)
    if location_id:
        filters.append(Diamond.location_id == location_id)
    if supplier_id:
        filters.append(Diamond.supplier_id == supplier_id)
    if diamond_type:
        filters.append(Diamond.diamond_type == diamond_type)

    base_query = db.query(Diamond)
    if filters:
        base_query = base_query.filter(and_(*filters))

    total = base_query.count()
    items = base_query.order_by(Diamond.created_at.desc()).offset(skip).limit(limit).all()

    # Hydrate location and supplier names
    results = []
    for item in items:
        item_dict = {
            "id": item.id,
            "sku": item.sku,
            "is_parcel": item.is_parcel,
            "lot_number": item.lot_number,
            "shape": item.shape,
            "carat_weight": item.carat_weight,
            "available_carats": item.available_carats,
            "color_grade": item.color_grade,
            "clarity_grade": item.clarity_grade,
            "cut_grade": item.cut_grade,
            "polish": item.polish,
            "symmetry": item.symmetry,
            "fluorescence": item.fluorescence,
            "measurements_mm": item.measurements_mm,
            "table_pct": item.table_pct,
            "depth_pct": item.depth_pct,
            "diamond_type": item.diamond_type,
            "treatment": item.treatment,
            "certificate_lab": item.certificate_lab,
            "certificate_number": item.certificate_number,
            "certificate_url": item.certificate_url,
            "purchase_cost": item.purchase_cost,
            "calculated_acquisition_cost": item.calculated_acquisition_cost,
            "asking_price": item.asking_price,
            "min_selling_price": item.min_selling_price,
            "status": item.status,
            "location_id": item.location_id,
            "supplier_id": item.supplier_id,
            "notes": item.notes,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "location_name": item.location.name if item.location else None,
            "supplier_name": item.supplier.business_name if item.supplier else None,
        }
        results.append(item_dict)

    return {"items": results, "total": total}

def get_diamond_by_id(db: Session, diamond_id: str) -> Optional[Diamond]:
    return db.query(Diamond).filter(Diamond.id == diamond_id).first()

def get_diamond_by_sku(db: Session, sku: str) -> Optional[Diamond]:
    return db.query(Diamond).filter(Diamond.sku == sku).first()

def create_diamond(db: Session, diamond_in: DiamondCreate, user_id: str) -> Diamond:
    # 1. Enforce unique SKU
    existing = get_diamond_by_sku(db, diamond_in.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Diamond with SKU '{diamond_in.sku}' already exists"
        )
    
    # 2. Enforce unique Certificate Number if provided
    if diamond_in.certificate_number:
        cert_exist = db.query(Diamond).filter(
            Diamond.certificate_number == diamond_in.certificate_number,
            Diamond.certificate_lab == diamond_in.certificate_lab
        ).first()
        if cert_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Diamond with Certificate '{diamond_in.certificate_lab}-{diamond_in.certificate_number}' already exists (SKU: {cert_exist.sku})"
            )

    data = diamond_in.model_dump()
    if data.get("available_carats") is None:
        data["available_carats"] = data["carat_weight"]
    if data.get("calculated_acquisition_cost") is None:
        data["calculated_acquisition_cost"] = data["purchase_cost"]

    diamond = Diamond(**data)
    db.add(diamond)
    db.flush()

    # Record opening stock movement
    record_movement(
        db=db,
        item_type="DIAMOND",
        diamond_id=diamond.id,
        movement_type="OPENING_STOCK",
        user_id=user_id,
        qty_before=0,
        qty_change=1,
        qty_after=1,
        carat_change=diamond.carat_weight,
        destination_location_id=diamond.location_id,
        reason=f"Registered in stock: {diamond.sku}"
    )

    log_audit_event(
        db=db,
        table_name="diamonds",
        record_id=diamond.id,
        action="CREATE",
        user_id=user_id,
        new_values=data,
        description=f"Created diamond {diamond.sku} ({diamond.carat_weight}ct {diamond.shape})"
    )

    db.commit()
    db.refresh(diamond)
    return diamond

def update_diamond(db: Session, diamond_id: str, diamond_in: DiamondUpdate, user_id: str) -> Diamond:
    diamond = get_diamond_by_id(db, diamond_id)
    if not diamond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diamond not found")

    old_data = {
        "status": diamond.status,
        "location_id": diamond.location_id,
        "asking_price": str(diamond.asking_price),
        "carat_weight": str(diamond.carat_weight)
    }

    update_data = diamond_in.model_dump(exclude_unset=True)
    
    # Check if location changed -> record movement
    if "location_id" in update_data and update_data["location_id"] != diamond.location_id:
        record_movement(
            db=db,
            item_type="DIAMOND",
            diamond_id=diamond.id,
            movement_type="LOCATION_TRANSFER",
            user_id=user_id,
            qty_before=1,
            qty_change=0,
            qty_after=1,
            source_location_id=diamond.location_id,
            destination_location_id=update_data["location_id"],
            reason="Location transfer"
        )

    for field, val in update_data.items():
        setattr(diamond, field, val)

    log_audit_event(
        db=db,
        table_name="diamonds",
        record_id=diamond.id,
        action="UPDATE",
        user_id=user_id,
        old_values=old_data,
        new_values=update_data,
        description=f"Updated diamond {diamond.sku}"
    )

    db.commit()
    db.refresh(diamond)
    return diamond

def reserve_diamond(db: Session, diamond_id: str, customer_id: str, hours: int, user_id: str, notes: Optional[str] = None) -> ItemReservation:
    diamond = get_diamond_by_id(db, diamond_id)
    if not diamond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diamond not found")
    
    if not validate_inventory_transition(diamond.status, InventoryState.RESERVED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Diamond is currently in '{diamond.status}' state and cannot be reserved"
        )
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    diamond.status = InventoryState.RESERVED.value
    
    expires_at = datetime.now(timezone.utc) + timedelta(hours=hours) if hours > 0 else None
    reservation = ItemReservation(
        item_type="DIAMOND",
        diamond_id=diamond.id,
        customer_id=customer_id,
        reserved_by_user_id=user_id,
        expires_at=expires_at,
        status="ACTIVE",
        notes=notes
    )
    db.add(reservation)

    log_audit_event(
        db=db,
        table_name="diamonds",
        record_id=diamond.id,
        action="RESERVE",
        user_id=user_id,
        description=f"Reserved diamond {diamond.sku} for customer {customer.name}"
    )

    db.commit()
    db.refresh(reservation)
    return reservation

def release_reservation(db: Session, diamond_id: str, user_id: str) -> Diamond:
    diamond = get_diamond_by_id(db, diamond_id)
    if not diamond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diamond not found")

    # Find active reservation
    reservation = db.query(ItemReservation).filter(
        ItemReservation.diamond_id == diamond_id,
        ItemReservation.status == "ACTIVE"
    ).first()

    if reservation:
        reservation.status = "RELEASED"

    if not validate_inventory_transition(diamond.status, InventoryState.AVAILABLE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reservation cannot be released from '{diamond.status}' state"
        )
    diamond.status = InventoryState.AVAILABLE.value

    log_audit_event(
        db=db,
        table_name="diamonds",
        record_id=diamond.id,
        action="RELEASE_RESERVATION",
        user_id=user_id,
        description=f"Released reservation for diamond {diamond.sku}"
    )

    db.commit()
    db.refresh(diamond)
    return diamond

def adjust_diamond(db: Session, adjustment: DiamondAdjustment, user_id: str) -> Diamond:
    diamond = get_diamond_by_id(db, adjustment.diamond_id)
    if not diamond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diamond not found")

    old_status = diamond.status
    if adjustment.new_status:
        target_status = adjustment.new_status.upper()
        if not validate_inventory_transition(old_status, target_status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid inventory transition from '{old_status}' to '{target_status}'"
            )
        diamond.status = target_status

    if adjustment.new_location_id:
        source_loc = diamond.location_id
        diamond.location_id = adjustment.new_location_id
        record_movement(
            db=db,
            item_type="DIAMOND",
            diamond_id=diamond.id,
            movement_type="LOCATION_TRANSFER",
            user_id=user_id,
            qty_before=1,
            qty_change=0,
            qty_after=1,
            source_location_id=source_loc,
            destination_location_id=adjustment.new_location_id,
            reason=adjustment.reason
        )

    if adjustment.carat_change and adjustment.carat_change != Decimal("0.0000"):
        diamond.carat_weight += adjustment.carat_change
        if diamond.available_carats:
            diamond.available_carats += adjustment.carat_change
        record_movement(
            db=db,
            item_type="DIAMOND",
            diamond_id=diamond.id,
            movement_type="STOCK_ADJUSTMENT",
            user_id=user_id,
            qty_before=1,
            qty_change=0,
            qty_after=1,
            carat_change=adjustment.carat_change,
            reason=adjustment.reason
        )

    log_audit_event(
        db=db,
        table_name="diamonds",
        record_id=diamond.id,
        action="ADJUSTMENT",
        user_id=user_id,
        description=f"Stock adjustment on {diamond.sku}: {adjustment.reason}"
    )

    db.commit()
    db.refresh(diamond)
    return diamond
