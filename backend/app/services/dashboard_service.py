from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.diamond import Diamond
from app.models.jewellery import JewelleryItem, JewelleryProduct
from app.models.gemstone import Gemstone
from app.models.sale import SalesOrder, SalesOrderItem
from app.models.purchase import PurchaseOrder
from app.models.invoice_payment import Invoice, Payment
from app.models.stock_movement import StockMovement

def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
    # 1. Inventory Summary (Live Aggregations)
    active_diamonds = db.query(Diamond).filter(Diamond.status == "AVAILABLE").all()
    dia_count = len(active_diamonds)
    dia_carats = sum([d.available_carats or d.carat_weight for d in active_diamonds], Decimal("0.0000"))
    dia_cost = sum([d.calculated_acquisition_cost or d.purchase_cost for d in active_diamonds], Decimal("0.00"))
    dia_asking = sum([d.asking_price for d in active_diamonds], Decimal("0.00"))

    active_jewellery = db.query(JewelleryItem).filter(JewelleryItem.status == "AVAILABLE").all()
    jwl_count = len(active_jewellery)
    jwl_weight = sum([j.gross_weight_grams for j in active_jewellery], Decimal("0.0000"))
    jwl_cost = sum([j.total_cost for j in active_jewellery], Decimal("0.00"))
    jwl_asking = sum([j.selling_price for j in active_jewellery], Decimal("0.00"))

    active_gems = db.query(Gemstone).filter(Gemstone.status == "AVAILABLE").all()
    gem_count = len(active_gems)
    gem_carats = sum([g.carat_weight for g in active_gems], Decimal("0.0000"))
    gem_cost = sum([g.purchase_cost for g in active_gems], Decimal("0.00"))
    gem_asking = sum([g.selling_price for g in active_gems], Decimal("0.00"))

    total_cost_val = dia_cost + jwl_cost + gem_cost
    total_asking_val = dia_asking + jwl_asking + gem_asking

    reserved_count = (
        db.query(Diamond).filter(Diamond.status == "RESERVED").count() +
        db.query(JewelleryItem).filter(JewelleryItem.status == "RESERVED").count() +
        db.query(Gemstone).filter(Gemstone.status == "RESERVED").count()
    )

    # 2. Business Summary (Current Month)
    now = datetime.now(timezone.utc)
    start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    month_sales = db.query(SalesOrder).filter(
        and_(SalesOrder.created_at >= start_of_month, SalesOrder.status != "CANCELLED")
    ).all()
    sales_rev_month = sum([s.total_amount for s in month_sales], Decimal("0.00"))
    sales_count_month = len(month_sales)

    month_pos = db.query(PurchaseOrder).filter(
        and_(PurchaseOrder.created_at >= start_of_month, PurchaseOrder.status != "CANCELLED")
    ).all()
    pos_total_month = sum([p.total_amount for p in month_pos], Decimal("0.00"))

    # COGS and Gross Profit calculation from sold order items this month
    gross_profit_month = Decimal("0.00")
    for s in month_sales:
        for it in s.items:
            cogs = it.cost_price * it.quantity
            profit = it.line_total - cogs
            gross_profit_month += profit

    gross_margin_pct = Decimal("0.00")
    if sales_rev_month > Decimal("0.00"):
        gross_margin_pct = ((gross_profit_month / sales_rev_month) * Decimal("100.0")).quantize(Decimal("0.1"))

    # Outstanding Receivables & Payables
    unpaid_invoices = db.query(Invoice).filter(Invoice.status.in_(["ISSUED", "PARTIALLY_PAID"])).all()
    receivables = sum([inv.balance_due for inv in unpaid_invoices], Decimal("0.00"))

    unpaid_pos = db.query(PurchaseOrder).filter(PurchaseOrder.payment_status.in_(["UNPAID", "PARTIALLY_PAID"])).all()
    payables = sum([p.total_amount - p.amount_paid for p in unpaid_pos], Decimal("0.00"))

    # 3. Recent Sales (Last 5)
    recent_sos = db.query(SalesOrder).order_by(SalesOrder.created_at.desc()).limit(5).all()
    recent_sales = [
        {
            "id": s.id,
            "so_number": s.so_number,
            "customer_name": s.customer.name if s.customer else "Counter",
            "date": s.sales_date.strftime("%d %b %Y"),
            "amount": float(s.total_amount),
            "status": s.status,
            "payment_status": s.payment_status
        } for s in recent_sos
    ]

    # 4. Recent Stock Movements (Last 5)
    recent_movs = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(5).all()
    recent_movements = [
        {
            "id": m.id,
            "movement_number": m.movement_number,
            "item_type": m.item_type,
            "movement_type": m.movement_type,
            "qty_change": m.qty_change,
            "reason": m.reason or "-",
            "date": m.created_at.strftime("%d %b %H:%M")
        } for m in recent_movs
    ]

    # 5. Inventory Category Breakdown for Charts
    category_counts = [
        {"name": "Solitaire Diamonds", "value": dia_count, "carats": float(dia_carats)},
        {"name": "Rings & Solitaires", "value": db.query(JewelleryItem).join(JewelleryProduct).filter(JewelleryProduct.category == "Ring", JewelleryItem.status == "AVAILABLE").count(), "weight": 0},
        {"name": "Necklaces", "value": db.query(JewelleryItem).join(JewelleryProduct).filter(JewelleryProduct.category == "Necklace", JewelleryItem.status == "AVAILABLE").count(), "weight": 0},
        {"name": "Earrings", "value": db.query(JewelleryItem).join(JewelleryProduct).filter(JewelleryProduct.category == "Earrings", JewelleryItem.status == "AVAILABLE").count(), "weight": 0},
        {"name": "Bangles & Bracelets", "value": db.query(JewelleryItem).join(JewelleryProduct).filter(JewelleryProduct.category.in_(["Bangles", "Bracelet"]), JewelleryItem.status == "AVAILABLE").count(), "weight": 0},
        {"name": "Loose Gemstones", "value": gem_count, "carats": float(gem_carats)}
    ]

    # 6. Sales Trend (Past 6 Months)
    sales_trend = []
    for i in range(5, -1, -1):
        m_date = now - timedelta(days=i*30)
        m_start = datetime(m_date.year, m_date.month, 1, tzinfo=timezone.utc)
        if m_date.month == 12:
            m_end = datetime(m_date.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            m_end = datetime(m_date.year, m_date.month + 1, 1, tzinfo=timezone.utc)
        
        m_sales = db.query(SalesOrder).filter(
            and_(SalesOrder.created_at >= m_start, SalesOrder.created_at < m_end, SalesOrder.status != "CANCELLED")
        ).all()
        m_rev = sum([s.total_amount for s in m_sales], Decimal("0.00"))
        sales_trend.append({
            "month": m_start.strftime("%b %Y"),
            "revenue": float(m_rev),
            "orders": len(m_sales)
        })

    return {
        "inventory": {
            "total_diamonds": dia_count,
            "total_diamond_carats": dia_carats,
            "total_jewellery_pieces": jwl_count,
            "total_jewellery_gross_weight_grams": jwl_weight,
            "total_gemstones": gem_count,
            "total_gemstone_carats": gem_carats,
            "total_cost_valuation": total_cost_val,
            "total_asking_valuation": total_asking_val,
            "reserved_items_count": reserved_count
        },
        "business": {
            "sales_count_month": sales_count_month,
            "sales_revenue_month": sales_rev_month,
            "purchases_total_month": pos_total_month,
            "gross_profit_month": gross_profit_month,
            "gross_margin_pct": gross_margin_pct,
            "outstanding_receivables": receivables,
            "outstanding_payables": payables
        },
        "recent_sales": recent_sales,
        "recent_movements": recent_movements,
        "category_distribution": category_counts,
        "sales_trend": sales_trend
    }
