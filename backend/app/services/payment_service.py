from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.invoice_payment import Invoice, Payment
from app.models.purchase import PurchaseOrder
from app.models.sale import SalesOrder
from app.schemas.invoice_payment import PaymentCreate
from app.services.audit_service import log_audit_event

def generate_payment_number(db: Session) -> str:
    count = db.query(Payment).count() + 1
    return f"PAY-{datetime.now(timezone.utc).year}-{count:04d}"

def get_invoices(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    query = db.query(Invoice)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    total = query.count()
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for inv in invoices:
        results.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "sales_order_id": inv.sales_order_id,
            "customer_id": inv.customer_id,
            "customer_name": inv.customer.name if inv.customer else None,
            "subtotal": inv.subtotal,
            "cgst_rate": inv.cgst_rate,
            "cgst_amount": inv.cgst_amount,
            "sgst_rate": inv.sgst_rate,
            "sgst_amount": inv.sgst_amount,
            "igst_rate": inv.igst_rate,
            "igst_amount": inv.igst_amount,
            "total_tax": inv.total_tax,
            "discount_amount": inv.discount_amount,
            "grand_total": inv.grand_total,
            "amount_paid": inv.amount_paid,
            "balance_due": inv.balance_due,
            "status": inv.status,
            "payment_terms": inv.payment_terms,
            "notes": inv.notes,
            "created_at": inv.created_at,
            "updated_at": inv.updated_at
        })

    return {"items": results, "total": total}

def get_payments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    payment_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    supplier_id: Optional[str] = None
) -> Dict[str, Any]:
    query = db.query(Payment)
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    if supplier_id:
        query = query.filter(Payment.supplier_id == supplier_id)

    total = query.count()
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for p in payments:
        results.append({
            "id": p.id,
            "payment_number": p.payment_number,
            "payment_date": p.payment_date,
            "payment_type": p.payment_type,
            "invoice_id": p.invoice_id,
            "invoice_number": p.invoice.invoice_number if p.invoice else None,
            "purchase_order_id": p.purchase_order_id,
            "po_number": p.purchase_order.po_number if hasattr(p, "purchase_order") and p.purchase_order else None,
            "customer_id": p.customer_id,
            "customer_name": p.customer.name if p.customer else None,
            "supplier_id": p.supplier_id,
            "supplier_name": p.supplier.business_name if p.supplier else None,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "reference_number": p.reference_number,
            "recorded_by_user_id": p.recorded_by_user_id,
            "recorder_name": p.user.full_name if p.user else None,
            "notes": p.notes,
            "created_at": p.created_at
        })

    return {"items": results, "total": total}

def record_payment(db: Session, payment_in: PaymentCreate, user_id: str) -> Payment:
    payment_number = generate_payment_number(db)

    # 1. Handling Customer Payment against Invoice
    if payment_in.payment_type == "CUSTOMER_PAYMENT" and payment_in.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == payment_in.invoice_id).with_for_update().first()
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

        if invoice.balance_due <= Decimal("0.00"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invoice is already fully settled")

        if payment_in.amount > invoice.balance_due:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount ₹{payment_in.amount:,.2f} exceeds outstanding balance of ₹{invoice.balance_due:,.2f}"
            )

        invoice.amount_paid += payment_in.amount
        invoice.balance_due -= payment_in.amount
        if invoice.balance_due <= Decimal("0.00"):
            invoice.status = "PAID"
        else:
            invoice.status = "PARTIALLY_PAID"

        # Update associated Sales Order
        if invoice.sales_order:
            invoice.sales_order.amount_paid += payment_in.amount
            if invoice.sales_order.amount_paid >= invoice.sales_order.total_amount:
                invoice.sales_order.payment_status = "PAID"
            else:
                invoice.sales_order.payment_status = "PARTIALLY_PAID"

        cust_id = invoice.customer_id
        supp_id = None

    # 2. Handling Supplier Payment against PO
    elif payment_in.payment_type == "SUPPLIER_PAYMENT" and payment_in.purchase_order_id:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == payment_in.purchase_order_id).with_for_update().first()
        if not po:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")

        outstanding = po.total_amount - po.amount_paid
        if payment_in.amount > outstanding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount ₹{payment_in.amount:,.2f} exceeds outstanding balance of ₹{outstanding:,.2f}"
            )

        po.amount_paid += payment_in.amount
        if po.amount_paid >= po.total_amount:
            po.payment_status = "PAID"
        else:
            po.payment_status = "PARTIALLY_PAID"

        cust_id = None
        supp_id = po.supplier_id

    else:
        cust_id = payment_in.customer_id
        supp_id = payment_in.supplier_id

    payment = Payment(
        payment_number=payment_number,
        payment_date=datetime.now(timezone.utc),
        payment_type=payment_in.payment_type,
        invoice_id=payment_in.invoice_id,
        purchase_order_id=payment_in.purchase_order_id,
        customer_id=cust_id,
        supplier_id=supp_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        reference_number=payment_in.reference_number,
        recorded_by_user_id=user_id,
        notes=payment_in.notes
    )
    db.add(payment)

    log_audit_event(
        db=db,
        table_name="payments",
        record_id=payment.id,
        action="RECORD_PAYMENT",
        user_id=user_id,
        description=f"Recorded {payment.payment_type} of ₹{payment.amount:,.2f} ({payment.payment_method})"
    )

    db.commit()
    db.refresh(payment)
    return payment
