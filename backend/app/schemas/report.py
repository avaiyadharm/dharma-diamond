from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

class InventorySummaryStats(BaseModel):
    total_diamonds: int
    total_diamond_carats: Decimal
    total_jewellery_pieces: int
    total_jewellery_gross_weight_grams: Decimal
    total_gemstones: int
    total_gemstone_carats: Decimal
    total_cost_valuation: Decimal
    total_asking_valuation: Decimal
    reserved_items_count: int

class BusinessSummaryStats(BaseModel):
    sales_count_month: int
    sales_revenue_month: Decimal
    purchases_total_month: Decimal
    gross_profit_month: Decimal
    gross_margin_pct: Decimal
    outstanding_receivables: Decimal
    outstanding_payables: Decimal

class DashboardData(BaseModel):
    inventory: InventorySummaryStats
    business: BusinessSummaryStats
    recent_sales: List[Dict[str, Any]] = []
    recent_movements: List[Dict[str, Any]] = []
    sales_trend: List[Dict[str, Any]] = []
    category_distribution: List[Dict[str, Any]] = []

class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
