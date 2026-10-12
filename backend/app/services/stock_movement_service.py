import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app.models.stock_movement import StockMovement

def generate_movement_number(db: Session) -> str:
    count = db.query(StockMovement).count() + 1
    return f"MOV-{datetime.now(timezone.utc).year}-{count:05d}"

def record_movement(
    db: Session,
    item_type: str,  # DIAMOND, JEWELLERY, GEMSTONE
    movement_type: str,  # OPENING_STOCK, PURCHASE_RECEIPT, SALE, CUSTOMER_RETURN, SUPPLIER_RETURN, LOCATION_TRANSFER, STOCK_ADJUSTMENT, MOUNTED_IN_JEWELLERY, DISMANTLED
    user_id: str,
    qty_before: int,
    qty_change: int,
    qty_after: int,
    diamond_id: Optional[str] = None,
    jewellery_item_id: Optional[str] = None,
    gemstone_id: Optional[str] = None,
    carat_change: Optional[Decimal] = None,
    weight_change_grams: Optional[Decimal] = None,
    source_location_id: Optional[str] = None,
    destination_location_id: Optional[str] = None,
    reference_doc_type: Optional[str] = None,
    reference_doc_id: Optional[str] = None,
    reason: Optional[str] = None
) -> StockMovement:
    movement_num = generate_movement_number(db)
    movement = StockMovement(
        movement_number=movement_num,
        item_type=item_type,
        diamond_id=diamond_id,
        jewellery_item_id=jewellery_item_id,
        gemstone_id=gemstone_id,
        movement_type=movement_type,
        qty_before=qty_before,
        qty_change=qty_change,
        qty_after=qty_after,
        carat_change=carat_change,
        weight_change_grams=weight_change_grams,
        source_location_id=source_location_id,
        destination_location_id=destination_location_id,
        reference_doc_type=reference_doc_type,
        reference_doc_id=reference_doc_id,
        user_id=user_id,
        reason=reason
    )
    db.add(movement)
    return movement
