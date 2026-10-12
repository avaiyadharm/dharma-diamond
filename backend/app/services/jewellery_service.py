from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status

from app.models.jewellery import JewelleryProduct, JewelleryItem, JewelleryStone
from app.models.diamond import Diamond
from app.models.sale import ItemReservation
from app.models.party import Customer
from app.schemas.jewellery import (
    JewelleryProductCreate, JewelleryProductUpdate,
    JewelleryItemCreate, JewelleryItemUpdate, JewelleryStoneCreate
)
from app.services.stock_movement_service import record_movement
from app.services.audit_service import log_audit_event

# --- Master Product / Design Catalog ---
def get_jewellery_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    metal_type: Optional[str] = None,
    purity: Optional[str] = None,
    query: Optional[str] = None
) -> Dict[str, Any]:
    filters = []
    if category:
        filters.append(JewelleryProduct.category == category)
    if metal_type:
        filters.append(JewelleryProduct.metal_type == metal_type)
    if purity:
        filters.append(JewelleryProduct.purity == purity)
    if query:
        q = f"%{query.strip()}%"
        filters.append(
            or_(
                JewelleryProduct.design_code.ilike(q),
                JewelleryProduct.name.ilike(q),
                JewelleryProduct.collection.ilike(q),
                JewelleryProduct.description.ilike(q)
            )
        )
    
    base_query = db.query(JewelleryProduct)
    if filters:
        base_query = base_query.filter(and_(*filters))
    
    total = base_query.count()
    products = base_query.order_by(JewelleryProduct.created_at.desc()).offset(skip).limit(limit).all()

    items = []
    for prod in products:
        items.append({
            "id": prod.id,
            "design_code": prod.design_code,
            "name": prod.name,
            "category": prod.category,
            "collection": prod.collection,
            "metal_type": prod.metal_type,
            "purity": prod.purity,
            "description": prod.description,
            "image_url": prod.image_url,
            "created_at": prod.created_at,
            "updated_at": prod.updated_at,
            "item_count": len(prod.items)
        })

    return {"items": items, "total": total}

def create_jewellery_product(db: Session, product_in: JewelleryProductCreate, user_id: str) -> JewelleryProduct:
    existing = db.query(JewelleryProduct).filter(JewelleryProduct.design_code == product_in.design_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Design with code '{product_in.design_code}' already exists"
        )
    prod = JewelleryProduct(**product_in.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)

    log_audit_event(
        db=db,
        table_name="jewellery_products",
        record_id=prod.id,
        action="CREATE",
        user_id=user_id,
        description=f"Created design {prod.design_code} - {prod.name}"
    )
    return prod

def get_jewellery_product_by_id(db: Session, product_id: str) -> Optional[JewelleryProduct]:
    return db.query(JewelleryProduct).filter(JewelleryProduct.id == product_id).first()

# --- Physical Jewellery Items ---
def get_jewellery_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    metal_type: Optional[str] = None,
    status: Optional[str] = None,
    location_id: Optional[str] = None,
    product_id: Optional[str] = None,
    query: Optional[str] = None
) -> Dict[str, Any]:
    query_builder = db.query(JewelleryItem).join(JewelleryProduct)

    filters = []
    if category:
        filters.append(JewelleryProduct.category == category)
    if metal_type:
        filters.append(JewelleryProduct.metal_type == metal_type)
    if status:
        filters.append(JewelleryItem.status == status)
    if location_id:
        filters.append(JewelleryItem.location_id == location_id)
    if product_id:
        filters.append(JewelleryItem.product_id == product_id)
    if query:
        q = f"%{query.strip()}%"
        filters.append(
            or_(
                JewelleryItem.sku.ilike(q),
                JewelleryProduct.name.ilike(q),
                JewelleryProduct.design_code.ilike(q),
                JewelleryItem.notes.ilike(q)
            )
        )

    if filters:
        query_builder = query_builder.filter(and_(*filters))

    total = query_builder.count()
    items = query_builder.order_by(JewelleryItem.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for it in items:
        results.append({
            "id": it.id,
            "sku": it.sku,
            "product_id": it.product_id,
            "gross_weight_grams": it.gross_weight_grams,
            "net_metal_weight_grams": it.net_metal_weight_grams,
            "total_stone_carats": it.total_stone_carats,
            "hallmark_details": it.hallmark_details,
            "metal_cost": it.metal_cost,
            "stone_cost": it.stone_cost,
            "making_charge": it.making_charge,
            "other_costs": it.other_costs,
            "total_cost": it.total_cost,
            "selling_price": it.selling_price,
            "status": it.status,
            "location_id": it.location_id,
            "supplier_id": it.supplier_id,
            "image_url": it.image_url or it.product.image_url,
            "notes": it.notes,
            "created_at": it.created_at,
            "updated_at": it.updated_at,
            "product_name": it.product.name,
            "product_category": it.product.category,
            "design_code": it.product.design_code,
            "metal_type": it.product.metal_type,
            "purity": it.product.purity,
            "location_name": it.location.name if it.location else None,
            "supplier_name": it.supplier.business_name if it.supplier else None,
            "stones": [
                {
                    "id": st.id,
                    "jewellery_item_id": st.jewellery_item_id,
                    "stone_type": st.stone_type,
                    "diamond_id": st.diamond_id,
                    "stone_count": st.stone_count,
                    "carat_weight": st.carat_weight,
                    "shape": st.shape,
                    "color": st.color,
                    "clarity": st.clarity,
                    "setting_type": st.setting_type,
                    "created_at": st.created_at,
                    "updated_at": st.updated_at
                } for st in it.stones
            ]
        })

    return {"items": results, "total": total}

def get_jewellery_item_by_id(db: Session, item_id: str) -> Optional[JewelleryItem]:
    return db.query(JewelleryItem).filter(JewelleryItem.id == item_id).first()

def get_jewellery_item_by_sku(db: Session, sku: str) -> Optional[JewelleryItem]:
    return db.query(JewelleryItem).filter(JewelleryItem.sku == sku).first()

def create_jewellery_item(db: Session, item_in: JewelleryItemCreate, user_id: str) -> JewelleryItem:
    # 1. Enforce unique SKU
    existing = get_jewellery_item_by_sku(db, item_in.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Jewellery item with SKU '{item_in.sku}' already exists"
        )

    # 2. Check product exists
    product = get_jewellery_product_by_id(db, item_in.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Master jewellery product not found")

    item_data = item_in.model_dump(exclude={"stones"})
    item = JewelleryItem(**item_data)
    db.add(item)
    db.flush()

    # Add stones if provided
    total_stone_carats = Decimal("0.0000")
    if item_in.stones:
        for st_data in item_in.stones:
            stone = JewelleryStone(
                jewellery_item_id=item.id,
                **st_data.model_dump()
            )
            db.add(stone)
            total_stone_carats += st_data.carat_weight
            
            # If a mounted diamond was linked, update diamond status to MOUNTED
            if st_data.diamond_id:
                dia = db.query(Diamond).filter(Diamond.id == st_data.diamond_id).first()
                if dia:
                    dia.status = "MOUNTED"
                    record_movement(
                        db=db,
                        item_type="DIAMOND",
                        diamond_id=dia.id,
                        movement_type="MOUNTED_IN_JEWELLERY",
                        user_id=user_id,
                        qty_before=1,
                        qty_change=-1,
                        qty_after=0,
                        carat_change=-dia.carat_weight,
                        reference_doc_type="JEWELLERY",
                        reference_doc_id=item.sku,
                        reason=f"Mounted into jewellery piece {item.sku}"
                    )

    item.total_stone_carats = total_stone_carats

    # Record opening stock movement for jewellery piece
    record_movement(
        db=db,
        item_type="JEWELLERY",
        jewellery_item_id=item.id,
        movement_type="OPENING_STOCK",
        user_id=user_id,
        qty_before=0,
        qty_change=1,
        qty_after=1,
        weight_change_grams=item.gross_weight_grams,
        destination_location_id=item.location_id,
        reason=f"Registered jewellery item: {item.sku} ({product.name})"
    )

    log_audit_event(
        db=db,
        table_name="jewellery_items",
        record_id=item.id,
        action="CREATE",
        user_id=user_id,
        description=f"Created jewellery item {item.sku} under {product.name}"
    )

    db.commit()
    db.refresh(item)
    return item

def update_jewellery_item(db: Session, item_id: str, item_in: JewelleryItemUpdate, user_id: str) -> JewelleryItem:
    item = get_jewellery_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jewellery item not found")

    update_data = item_in.model_dump(exclude_unset=True)

    if "location_id" in update_data and update_data["location_id"] != item.location_id:
        record_movement(
            db=db,
            item_type="JEWELLERY",
            jewellery_item_id=item.id,
            movement_type="LOCATION_TRANSFER",
            user_id=user_id,
            qty_before=1,
            qty_change=0,
            qty_after=1,
            source_location_id=item.location_id,
            destination_location_id=update_data["location_id"],
            reason="Location transfer"
        )

    for field, val in update_data.items():
        setattr(item, field, val)

    log_audit_event(
        db=db,
        table_name="jewellery_items",
        record_id=item.id,
        action="UPDATE",
        user_id=user_id,
        description=f"Updated jewellery item {item.sku}"
    )

    db.commit()
    db.refresh(item)
    return item
