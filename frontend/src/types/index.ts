export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'inventory_manager' | 'sales_staff' | 'accountant' | 'read_only';
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface Location {
  id: string;
  code: string;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface Supplier {
  id: string;
  business_name: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  tax_id?: string;
  country: string;
  currency: string;
  payment_terms?: string;
  category: string;
  notes?: string;
  is_active: boolean;
  total_purchases?: number;
  total_paid?: number;
  outstanding_balance?: number;
  created_at: string;
}

export interface Customer {
  id: string;
  name: string;
  company_name?: string;
  phone?: string;
  email?: string;
  billing_address?: string;
  shipping_address?: string;
  tax_id?: string;
  customer_type: string;
  notes?: string;
  is_active: boolean;
  total_purchases?: number;
  total_paid?: number;
  outstanding_balance?: number;
  created_at: string;
}

export interface Diamond {
  id: string;
  sku: string;
  is_parcel: boolean;
  lot_number?: string;
  shape: string;
  carat_weight: number;
  available_carats?: number;
  color_grade: string;
  clarity_grade: string;
  cut_grade?: string;
  polish?: string;
  symmetry?: string;
  fluorescence?: string;
  measurements_mm?: string;
  table_pct?: number;
  depth_pct?: number;
  diamond_type: string;
  treatment?: string;
  certificate_lab: string;
  certificate_number?: string;
  certificate_url?: string;
  purchase_cost: number;
  calculated_acquisition_cost?: number;
  asking_price: number;
  min_selling_price?: number;
  status: 'AVAILABLE' | 'RESERVED' | 'SOLD' | 'MOUNTED' | 'RETURNED' | 'DAMAGED';
  location_id?: string;
  location_name?: string;
  supplier_id?: string;
  supplier_name?: string;
  notes?: string;
  created_at: string;
}

export interface JewelleryProduct {
  id: string;
  design_code: string;
  name: string;
  category: string;
  collection?: string;
  metal_type: string;
  purity: string;
  description?: string;
  image_url?: string;
  item_count?: number;
  created_at: string;
}

export interface JewelleryStone {
  id: string;
  jewellery_item_id?: string;
  stone_type: string;
  diamond_id?: string;
  stone_count: number;
  carat_weight: number;
  shape?: string;
  color?: string;
  clarity?: string;
  setting_type?: string;
}

export interface JewelleryItem {
  id: string;
  sku: string;
  product_id: string;
  product_name?: string;
  product_category?: string;
  design_code?: string;
  metal_type?: string;
  purity?: string;
  gross_weight_grams: number;
  net_metal_weight_grams: number;
  total_stone_carats: number;
  hallmark_details?: string;
  metal_cost: number;
  stone_cost: number;
  making_charge: number;
  other_costs: number;
  total_cost: number;
  selling_price: number;
  status: 'AVAILABLE' | 'RESERVED' | 'SOLD' | 'DISMANTLED' | 'DAMAGED';
  location_id?: string;
  location_name?: string;
  supplier_id?: string;
  supplier_name?: string;
  image_url?: string;
  notes?: string;
  stones?: JewelleryStone[];
  created_at: string;
}

export interface Gemstone {
  id: string;
  sku: string;
  gemstone_type: string;
  variety?: string;
  is_natural: boolean;
  carat_weight: number;
  shape: string;
  color: string;
  clarity?: string;
  cut?: string;
  treatment?: string;
  certificate_lab: string;
  certificate_number?: string;
  purchase_cost: number;
  selling_price: number;
  status: string;
  location_id?: string;
  location_name?: string;
  supplier_id?: string;
  supplier_name?: string;
  notes?: string;
  created_at: string;
}

export interface PurchaseOrderItem {
  id: string;
  item_type: string;
  description: string;
  quantity: number;
  carat_weight?: number;
  unit_price: number;
  line_total: number;
  received_quantity: number;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  supplier_id: string;
  supplier_name?: string;
  purchase_date: string;
  expected_delivery_date?: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  amount_paid: number;
  payment_status: string;
  status: string;
  notes?: string;
  items: PurchaseOrderItem[];
  created_at: string;
}

export interface SalesOrderItem {
  id: string;
  sales_order_id: string;
  item_type: string;
  diamond_id?: string;
  jewellery_item_id?: string;
  gemstone_id?: string;
  sku: string;
  description: string;
  quantity: number;
  unit_price: number;
  cost_price: number;
  discount: number;
  line_total: number;
}

export interface SalesOrder {
  id: string;
  so_number: string;
  customer_id: string;
  customer_name?: string;
  sales_date: string;
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  total_amount: number;
  amount_paid: number;
  payment_status: string;
  status: string;
  notes?: string;
  salesperson_name?: string;
  items: SalesOrderItem[];
  created_at: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  invoice_date: string;
  sales_order_id: string;
  customer_id: string;
  customer_name?: string;
  subtotal: number;
  cgst_rate: number;
  cgst_amount: number;
  sgst_rate: number;
  sgst_amount: number;
  igst_rate: number;
  igst_amount: number;
  total_tax: number;
  discount_amount: number;
  grand_total: number;
  amount_paid: number;
  balance_due: number;
  status: string;
  payment_terms?: string;
  notes?: string;
  created_at: string;
}

export interface Payment {
  id: string;
  payment_number: string;
  payment_date: string;
  payment_type: string;
  invoice_id?: string;
  invoice_number?: string;
  purchase_order_id?: string;
  po_number?: string;
  customer_id?: string;
  customer_name?: string;
  supplier_id?: string;
  supplier_name?: string;
  amount: number;
  payment_method: string;
  reference_number?: string;
  recorder_name?: string;
  notes?: string;
  created_at: string;
}

export interface StockMovement {
  id: string;
  movement_number: string;
  item_type: string;
  diamond_id?: string;
  jewellery_item_id?: string;
  gemstone_id?: string;
  movement_type: string;
  qty_before: number;
  qty_change: number;
  qty_after: number;
  carat_change?: number;
  weight_change_grams?: number;
  source_location_name?: string;
  destination_location_name?: string;
  reference_doc_type?: string;
  reference_doc_id?: string;
  user_name?: string;
  item_sku?: string;
  reason?: string;
  created_at: string;
}

export interface DashboardData {
  inventory: {
    total_diamonds: number;
    total_diamond_carats: number;
    total_jewellery_pieces: number;
    total_jewellery_gross_weight_grams: number;
    total_gemstones: number;
    total_gemstone_carats: number;
    total_cost_valuation: number;
    total_asking_valuation: number;
    reserved_items_count: number;
  };
  business: {
    sales_count_month: number;
    sales_revenue_month: number;
    purchases_total_month: number;
    gross_profit_month: number;
    gross_margin_pct: number;
    outstanding_receivables: number;
    outstanding_payables: number;
  };
  recent_sales: any[];
  recent_movements: any[];
  category_distribution: { name: string; value: number; carats?: number; weight?: number }[];
  sales_trend: { month: string; revenue: number; orders: number }[];
}

export interface AuditLog {
  id: string;
  table_name: string;
  record_id: string;
  action: string;
  old_values?: string;
  new_values?: string;
  user_name?: string;
  ip_address?: string;
  description?: string;
  created_at: string;
}
