from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.sale import SalesOrder, SalesOrderItem, ItemReservation
from app.models.invoice_payment import Invoice, Payment
from app.models.diamond import Diamond
from app.models.jewellery import JewelleryItem
from app.models.gemstone import Gemstone
from app.models.party import Customer
from app.schemas.sale import SalesOrderCreate
from app.services.stock_movement_service import record_movement
from app.services.audit_service import log_audit_event

def generate_so_number(db: Session) -> str:
    count = db.query(SalesOrder).count() + 1
    return f"SO-{datetime.now(timezone.utc).year}-{count:04d}"

def generate_invoice_number(db: Session) -> str:
    count = db.query(Invoice).count() + 1
    return f"INV-{datetime.now(timezone.utc).year}-{count:04d}"

def generate_payment_number(db: Session) -> str:
    count = db.query(Payment).count() + 1
    return f"RCPT-{datetime.now(timezone.utc).year}-{count:04d}"

def get_sales_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    query = db.query(SalesOrder)
    if customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)
    if status_filter:
        query = query.filter(SalesOrder.status == status_filter)

    total = query.count()
    sos = query.order_by(SalesOrder.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for so in sos:
        results.append({
            "id": so.id,
            "so_number": so.so_number,
            "customer_id": so.customer_id,
            "customer_name": so.customer.name if so.customer else None,
            "sales_date": so.sales_date,
            "subtotal": so.subtotal,
            "discount_amount": so.discount_amount,
            "tax_amount": so.tax_amount,
            "total_amount": so.total_amount,
            "amount_paid": so.amount_paid,
            "payment_status": so.payment_status,
            "status": so.status,
            "notes": so.notes,
            "created_by_user_id": so.created_by_user_id,
            "salesperson_name": so.salesperson.full_name if so.salesperson else None,
            "created_at": so.created_at,
            "updated_at": so.updated_at,
            "items": [
                {
                    "id": it.id,
                    "sales_order_id": it.sales_order_id,
                    "item_type": it.item_type,
                    "diamond_id": it.diamond_id,
                    "jewellery_item_id": it.jewellery_item_id,
                    "gemstone_id": it.gemstone_id,
                    "sku": it.sku,
                    "description": it.description,
                    "quantity": it.quantity,
                    "unit_price": it.unit_price,
                    "cost_price": it.cost_price,
                    "discount": it.discount,
                    "line_total": it.line_total,
                    "created_at": it.created_at
                } for it in so.items
            ]
        })

    return {"items": results, "total": total}

def create_sales_order(db: Session, so_in: SalesOrderCreate, user_id: str) -> SalesOrder:
    # 1. Customer verification
    customer = db.query(Customer).filter(Customer.id == so_in.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    if not so_in.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sales order must contain at least one item")

    so_number = generate_so_number(db)
    
    subtotal = Decimal("0.00")
    total_cost_basis = Decimal("0.00")
    prepared_items = []

    # 2. Atomic check and lock on each physical inventory item
    for item_data in so_in.items:
        unit_price = item_data.unit_price
        discount = item_data.discount or Decimal("0.00")
        line_total = (unit_price * item_data.quantity) - discount
        subtotal += line_total
        cost_price = Decimal("0.00")

        if item_data.item_type == "DIAMOND":
            diamond = db.query(Diamond).filter(Diamond.id == item_data.diamond_id).with_for_update().first()
            if not diamond:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Diamond {item_data.sku} not found")
            
            # Check availability or customer reservation
            if diamond.status not in ["AVAILABLE", "RESERVED"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Diamond '{diamond.sku}' cannot be sold because its status is '{diamond.status}'"
                )
            
            cost_price = diamond.calculated_acquisition_cost or diamond.purchase_cost
            total_cost_basis += cost_price

            # Atomic status update
            diamond.status = "SOLD"
            record_movement(
                db=db,
                item_type="DIAMOND",
                diamond_id=diamond.id,
                movement_type="SALE",
                user_id=user_id,
                qty_before=1,
                qty_change=-1,
                qty_after=0,
                carat_change=-diamond.carat_weight,
                source_location_id=diamond.location_id,
                reference_doc_type="SALES_ORDER",
                reference_doc_id=so_number,
                reason=f"Sold to {customer.name} on {so_number}"
            )

        elif item_data.item_type == "JEWELLERY":
            jewellery = db.query(JewelleryItem).filter(JewelleryItem.id == item_data.jewellery_item_id).with_for_update().first()
            if not jewellery:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Jewellery piece {item_data.sku} not found")

            if jewellery.status not in ["AVAILABLE", "RESERVED"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Jewellery piece '{jewellery.sku}' cannot be sold because its status is '{jewellery.status}'"
                )

            cost_price = jewellery.total_cost
            total_cost_basis += cost_price

            jewellery.status = "SOLD"
            record_movement(
                db=db,
                item_type="JEWELLERY",
                jewellery_item_id=jewellery.id,
                movement_type="SALE",
                user_id=user_id,
                qty_before=1,
                qty_change=-1,
                qty_after=0,
                weight_change_grams=-jewellery.gross_weight_grams,
                source_location_id=jewellery.location_id,
                reference_doc_type="SALES_ORDER",
                reference_doc_id=so_number,
                reason=f"Sold to {customer.name} on {so_number}"
            )

        elif item_data.item_type == "GEMSTONE":
            gem = db.query(Gemstone).filter(Gemstone.id == item_data.gemstone_id).with_for_update().first()
            if not gem:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gemstone {item_data.sku} not found")

            if gem.status != "AVAILABLE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Gemstone '{gem.sku}' cannot be sold because its status is '{gem.status}'"
                )

            cost_price = gem.purchase_cost
            total_cost_basis += cost_price

            gem.status = "SOLD"
            record_movement(
                db=db,
                item_type="GEMSTONE",
                gemstone_id=gem.id,
                movement_type="SALE",
                user_id=user_id,
                qty_before=1,
                qty_change=-1,
                qty_after=0,
                carat_change=-gem.carat_weight,
                source_location_id=gem.location_id,
                reference_doc_type="SALES_ORDER",
                reference_doc_id=so_number,
                reason=f"Sold to {customer.name} on {so_number}"
            )

        prepared_items.append({
            "item_type": item_data.item_type,
            "diamond_id": item_data.diamond_id,
            "jewellery_item_id": item_data.jewellery_item_id,
            "gemstone_id": item_data.gemstone_id,
            "sku": item_data.sku,
            "description": item_data.description,
            "quantity": item_data.quantity,
            "unit_price": unit_price,
            "cost_price": cost_price,  # Captured snapshot for exact COGS
            "discount": discount,
            "line_total": line_total
        })

    # 3. Tax & Totals calculation
    subtotal_after_order_discount = max(Decimal("0.00"), subtotal - (so_in.discount_amount or Decimal("0.00")))
    tax_rate = so_in.tax_rate_pct / Decimal("100.0")
    tax_amount = (subtotal_after_order_discount * tax_rate).quantize(Decimal("0.01"))
    total_amount = subtotal_after_order_discount + tax_amount

    initial_payment = so_in.initial_payment_amount or Decimal("0.00")
    if initial_payment > total_amount:
        initial_payment = total_amount

    payment_status = "UNPAID"
    if initial_payment >= total_amount:
        payment_status = "PAID"
    elif initial_payment > 0:
        payment_status = "PARTIALLY_PAID"

    # 4. Create Sales Order
    sales_order = SalesOrder(
        so_number=so_number,
        customer_id=so_in.customer_id,
        sales_date=datetime.now(timezone.utc),
        subtotal=subtotal,
        discount_amount=so_in.discount_amount or Decimal("0.00"),
        tax_amount=tax_amount,
        total_amount=total_amount,
        amount_paid=initial_payment,
        payment_status=payment_status,
        status="CONFIRMED",
        created_by_user_id=user_id,
        notes=so_in.notes
    )
    db.add(sales_order)
    db.flush()

    for p_item in prepared_items:
        so_item = SalesOrderItem(
            sales_order_id=sales_order.id,
            **p_item
        )
        db.add(so_item)

    # 5. Automatically create official GST Invoice
    inv_number = generate_invoice_number(db)
    cgst_rate = Decimal("1.50")
    sgst_rate = Decimal("1.50")
    cgst_amt = (subtotal_after_order_discount * (cgst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
    sgst_amt = (subtotal_after_order_discount * (sgst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
    
    invoice = Invoice(
        invoice_number=inv_number,
        sales_order_id=sales_order.id,
        customer_id=customer.id,
        subtotal=subtotal,
        cgst_rate=cgst_rate,
        cgst_amount=cgst_amt,
        sgst_rate=sgst_rate,
        sgst_amount=sgst_amt,
        igst_rate=Decimal("0.00"),
        igst_amount=Decimal("0.00"),
        total_tax=tax_amount,
        discount_amount=so_in.discount_amount or Decimal("0.00"),
        grand_total=total_amount,
        amount_paid=initial_payment,
        balance_due=total_amount - initial_payment,
        status="PAID" if initial_payment >= total_amount else ("PARTIALLY_PAID" if initial_payment > 0 else "ISSUED"),
        payment_terms="Immediate",
        notes=so_in.notes
    )
    db.add(invoice)
    db.flush()

    # 6. Record Payment if initial payment provided
    if initial_payment > Decimal("0.00"):
        rcpt_num = generate_payment_number(db)
        payment = Payment(
            payment_number=rcpt_num,
            payment_type="CUSTOMER_PAYMENT",
            invoice_id=invoice.id,
            customer_id=customer.id,
            amount=initial_payment,
            payment_method=so_in.payment_method or "Bank Transfer",
            recorded_by_user_id=user_id,
            notes=f"Initial payment for {so_number}"
        )
        db.add(payment)

    log_audit_event(
        db=db,
        table_name="sales_orders",
        record_id=sales_order.id,
        action="CREATE_SALE",
        user_id=user_id,
        description=f"Finalized sale {so_number} for ₹{total_amount:,.2f} to {customer.name}"
    )

    db.commit()
    db.refresh(sales_order)
    return sales_order

def cancel_sales_order(db: Session, sales_order_id: str, reason: str, user_id: str) -> SalesOrder:
    so = db.query(SalesOrder).filter(SalesOrder.id == sales_order_id).first()
    if not so:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")

    if so.status in ["CANCELLED", "RETURNED"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Order is already in '{so.status}' status")

    # Reversal of inventory
    for item in so.items:
        if item.diamond_id:
            diamond = db.query(Diamond).filter(Diamond.id == item.diamond_id).first()
            if diamond:
                diamond.status = "AVAILABLE"
                record_movement(
                    db=db,
                    item_type="DIAMOND",
                    diamond_id=diamond.id,
                    movement_type="CUSTOMER_RETURN",
                    user_id=user_id,
                    qty_before=0,
                    qty_change=1,
                    qty_after=1,
                    carat_change=diamond.carat_weight,
                    destination_location_id=diamond.location_id,
                    reference_doc_type="SALES_CANCEL",
                    reference_doc_id=so.so_number,
                    reason=f"Sale cancelled: {reason}"
                )
        elif item.jewellery_item_id:
            jewellery = db.query(JewelleryItem).filter(JewelleryItem.id == item.jewellery_item_id).first()
            if jewellery:
                jewellery.status = "AVAILABLE"
                record_movement(
                    db=db,
                    item_type="JEWELLERY",
                    jewellery_item_id=jewellery.id,
                    movement_type="CUSTOMER_RETURN",
                    user_id=user_id,
                    qty_before=0,
                    qty_change=1,
                    qty_after=1,
                    weight_change_grams=jewellery.gross_weight_grams,
                    destination_location_id=jewellery.location_id,
                    reference_doc_type="SALES_CANCEL",
                    reference_doc_id=so.so_number,
                    reason=f"Sale cancelled: {reason}"
                )

    so.status = "CANCELLED"
    for inv in so.invoices:
        inv.status = "CANCELLED"

    log_audit_event(
        db=db,
        table_name="sales_orders",
        record_id=so.id,
        action="CANCEL",
        user_id=user_id,
        description=f"Cancelled sale {so.so_number}: {reason}"
    )

    db.commit()
    db.refresh(so)
    return so
