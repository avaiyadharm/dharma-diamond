import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.diamond import Diamond
from app.models.jewellery import JewelleryItem
from app.models.sale import SalesOrder
from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/export/diamonds.csv")
def export_diamonds_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diamonds = db.query(Diamond).all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "SKU", "Shape", "Carat Weight", "Color", "Clarity", "Cut", "Polish", "Symmetry",
        "Fluorescence", "Certificate Lab", "Certificate Number", "Purchase Cost (INR)",
        "Asking Price (INR)", "Status", "Location", "Supplier", "Date Added"
    ])

    for d in diamonds:
        writer.writerow([
            d.sku,
            d.shape,
            str(d.carat_weight),
            d.color_grade,
            d.clarity_grade,
            d.cut_grade or "-",
            d.polish or "-",
            d.symmetry or "-",
            d.fluorescence or "-",
            d.certificate_lab,
            d.certificate_number or "-",
            str(d.purchase_cost),
            str(d.asking_price),
            d.status,
            d.location.name if d.location else "-",
            d.supplier.business_name if d.supplier else "-",
            d.created_at.strftime("%Y-%m-%d")
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=dharma_diamonds_inventory.csv"}
    )

@router.get("/export/sales.csv")
def export_sales_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sales = db.query(SalesOrder).order_by(SalesOrder.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Order #", "Date", "Customer", "Subtotal (INR)", "Discount (INR)", "Tax (INR)",
        "Total (INR)", "Amount Paid (INR)", "Payment Status", "Order Status", "Items Count"
    ])

    for s in sales:
        writer.writerow([
            s.so_number,
            s.sales_date.strftime("%Y-%m-%d"),
            s.customer.name if s.customer else "-",
            str(s.subtotal),
            str(s.discount_amount),
            str(s.tax_amount),
            str(s.total_amount),
            str(s.amount_paid),
            s.payment_status,
            s.status,
            len(s.items)
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=dharma_sales_records.csv"}
    )
