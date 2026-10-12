from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.purchase import PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from app.models.party import Supplier
from app.schemas.purchase import PurchaseOrderCreate, PurchaseOrderUpdate, GoodsReceiptCreate
from app.services.stock_movement_service import record_movement
from app.services.audit_service import log_audit_event

def generate_po_number(db: Session) -> str:
    count = db.query(PurchaseOrder).count() + 1
    return f"PO-{datetime.now(timezone.utc).year}-{count:04d}"

def generate_receipt_number(db: Session) -> str:
    count = db.query(GoodsReceipt).count() + 1
    return f"GRN-{datetime.now(timezone.utc).year}-{count:04d}"

def get_purchase_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    query = db.query(PurchaseOrder)
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)

    total = query.count()
    pos = query.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for po in pos:
        results.append({
            "id": po.id,
            "po_number": po.po_number,
            "supplier_id": po.supplier_id,
            "supplier_name": po.supplier.business_name if po.supplier else None,
            "purchase_date": po.purchase_date,
            "expected_delivery_date": po.expected_delivery_date,
            "subtotal": po.subtotal,
            "tax_amount": po.tax_amount,
            "total_amount": po.total_amount,
            "amount_paid": po.amount_paid,
            "payment_status": po.payment_status,
            "status": po.status,
            "notes": po.notes,
            "created_at": po.created_at,
            "updated_at": po.updated_at,
            "items": [
                {
                    "id": it.id,
                    "purchase_order_id": it.purchase_order_id,
                    "item_type": it.item_type,
                    "description": it.description,
                    "quantity": it.quantity,
                    "carat_weight": it.carat_weight,
                    "unit_price": it.unit_price,
                    "line_total": it.line_total,
                    "received_quantity": it.received_quantity,
                    "created_at": it.created_at,
                    "updated_at": it.updated_at
                } for it in po.items
            ],
            "receipts": [
                {
                    "id": r.id,
                    "receipt_number": r.receipt_number,
                    "purchase_order_id": r.purchase_order_id,
                    "received_date": r.received_date,
                    "received_by_user_id": r.received_by_user_id,
                    "receiver_name": r.receiver.full_name if r.receiver else None,
                    "notes": r.notes,
                    "created_at": r.created_at
                } for r in po.receipts
            ]
        })

    return {"items": results, "total": total}

def create_purchase_order(db: Session, po_in: PurchaseOrderCreate, user_id: str) -> PurchaseOrder:
    supplier = db.query(Supplier).filter(Supplier.id == po_in.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    po_number = generate_po_number(db)
    
    subtotal = Decimal("0.00")
    for item in po_in.items:
        subtotal += item.line_total

    tax_rate = po_in.tax_rate_pct / Decimal("100.0")
    tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
    total_amount = subtotal + tax_amount

    po = PurchaseOrder(
        po_number=po_number,
        supplier_id=po_in.supplier_id,
        expected_delivery_date=po_in.expected_delivery_date,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        amount_paid=Decimal("0.00"),
        payment_status="UNPAID",
        status="CONFIRMED",
        notes=po_in.notes
    )
    db.add(po)
    db.flush()

    for it_in in po_in.items:
        po_item = PurchaseOrderItem(
            purchase_order_id=po.id,
            item_type=it_in.item_type,
            description=it_in.description,
            quantity=it_in.quantity,
            carat_weight=it_in.carat_weight,
            unit_price=it_in.unit_price,
            line_total=it_in.line_total,
            received_quantity=0
        )
        db.add(po_item)

    log_audit_event(
        db=db,
        table_name="purchase_orders",
        record_id=po.id,
        action="CREATE",
        user_id=user_id,
        description=f"Created PO {po.po_number} with {supplier.business_name} for ₹{po.total_amount:,.2f}"
    )

    db.commit()
    db.refresh(po)
    return po

def receive_goods(db: Session, receipt_in: GoodsReceiptCreate, user_id: str) -> GoodsReceipt:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == receipt_in.purchase_order_id).first()
    if not po:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")

    if po.status in ["RECEIVED", "CANCELLED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot receive goods for purchase order with status '{po.status}'"
        )

    receipt_num = generate_receipt_number(db)
    grn = GoodsReceipt(
        receipt_number=receipt_num,
        purchase_order_id=po.id,
        received_by_user_id=user_id,
        notes=receipt_in.notes
    )
    db.add(grn)
    db.flush()

    # Mark items as received
    all_received = True
    for item in po.items:
        needed = item.quantity - item.received_quantity
        if needed > 0:
            item.received_quantity += needed
            record_movement(
                db=db,
                item_type=item.item_type,
                movement_type="PURCHASE_RECEIPT",
                user_id=user_id,
                qty_before=0,
                qty_change=needed,
                qty_after=needed,
                carat_change=item.carat_weight,
                destination_location_id=receipt_in.location_id,
                reference_doc_type="PURCHASE_ORDER",
                reference_doc_id=po.po_number,
                reason=f"Received under {receipt_num}: {item.description}"
            )

    po.status = "RECEIVED"

    log_audit_event(
        db=db,
        table_name="goods_receipts",
        record_id=grn.id,
        action="RECEIVE",
        user_id=user_id,
        description=f"Confirmed Goods Receipt {receipt_num} for PO {po.po_number}"
    )

    db.commit()
    db.refresh(grn)
    return grn
