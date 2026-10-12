import React, { useEffect, useState } from 'react';
import {
  Gem,
  Sparkles,
  CircleDot,
  TrendingUp,
  Receipt,
  Scale,
  ArrowUpRight,
  Clock,
  ArrowRightLeft,
  DollarSign
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import api from '../api/client';
import type { DashboardData } from '../types';
import { formatCurrency, formatCarat, formatWeightGrams } from '../utils/formatters';
import { Badge } from '../components/common/Badge';

const PIE_COLORS = ['#C59A27', '#3B82F6', '#10B981', '#EC4899', '#8B5CF6', '#F59E0B'];

export const DashboardView: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dashboard');
      setData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-500">Calculating vault statistics from database...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 p-8">
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl">
          {error || 'Unable to display statistics'}
        </div>
      </div>
    );
  }

  const { inventory, business, recent_sales, recent_movements, sales_trend, category_distribution } = data;

  return (
    <div className="flex-1 p-8 space-y-8 overflow-y-auto">
      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Diamonds */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden group hover:border-amber-300 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Certified Diamonds</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Gem className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-800 font-serif">{inventory.total_diamonds} pcs</p>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
            <span>Total Weight:</span>
            <span className="font-semibold text-slate-700">{formatCarat(inventory.total_diamond_carats)}</span>
          </div>
        </div>

        {/* Finished Jewellery */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden group hover:border-amber-300 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Finished Jewellery</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-800 font-serif">{inventory.total_jewellery_pieces} pcs</p>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
            <span>Gross Stock Weight:</span>
            <span className="font-semibold text-slate-700">{formatWeightGrams(inventory.total_jewellery_gross_weight_grams)}</span>
          </div>
        </div>

        {/* Vault Cost Valuation */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden group hover:border-amber-300 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Inventory Cost (COGS Basis)</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Scale className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-800 font-serif">{formatCurrency(inventory.total_cost_valuation)}</p>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
            <span>Asking Retail Value:</span>
            <span className="font-semibold text-emerald-600">{formatCurrency(inventory.total_asking_valuation)}</span>
          </div>
        </div>

        {/* Month Sales & Gross Margin */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden group hover:border-amber-300 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Month Sales Revenue</span>
            <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-800 font-serif">{formatCurrency(business.sales_revenue_month)}</p>
          <div className="mt-2 flex items-center justify-between text-xs">
            <span className="text-slate-500">Gross Margin:</span>
            <span className="font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
              +{business.gross_margin_pct}% ({formatCurrency(business.gross_profit_month)})
            </span>
          </div>
        </div>
      </div>

      {/* Secondary Metrics Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-slate-900 text-white p-4 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Unpaid Customer Invoices</p>
            <p className="text-lg font-bold font-serif mt-1 text-amber-300">{formatCurrency(business.outstanding_receivables)}</p>
          </div>
          <Receipt className="w-6 h-6 text-slate-600" />
        </div>

        <div className="bg-slate-900 text-white p-4 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Outstanding Supplier Payables</p>
            <p className="text-lg font-bold font-serif mt-1 text-slate-200">{formatCurrency(business.outstanding_payables)}</p>
          </div>
          <Receipt className="w-6 h-6 text-slate-600" />
        </div>

        <div className="bg-slate-900 text-white p-4 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Currently Reserved Items</p>
            <p className="text-lg font-bold font-serif mt-1 text-amber-400">{inventory.reserved_items_count} items held</p>
          </div>
          <Clock className="w-6 h-6 text-slate-600" />
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 6-Month Sales Trend */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-serif font-bold text-slate-800 text-base">Sales Revenue Trend</h3>
              <p className="text-xs text-slate-500">Past 6 months actual closed sales (INR)</p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sales_trend}>
                <defs>
                  <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#C59A27" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#C59A27" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="month" stroke="#64748B" fontSize={11} />
                <YAxis
                  stroke="#64748B"
                  fontSize={11}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(value: any) => [formatCurrency(value), 'Revenue']}
                  contentStyle={{ backgroundColor: '#0F172A', color: '#FFF', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#C59A27" strokeWidth={2.5} fillOpacity={1} fill="url(#goldGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Inventory Category Breakdown */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm">
          <h3 className="font-serif font-bold text-slate-800 text-base mb-1">Inventory Breakdown</h3>
          <p className="text-xs text-slate-500 mb-4">Stock count by jewellery category</p>
          <div className="h-44 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={category_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={65}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {category_distribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any, name: any) => [`${val} pcs`, name]}
                  contentStyle={{ backgroundColor: '#0F172A', color: '#FFF', borderRadius: '8px', fontSize: '11px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 space-y-1.5 max-h-24 overflow-y-auto">
            {category_distribution.map((c, i) => (
              <div key={c.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }} />
                  <span className="text-slate-600 truncate max-w-[140px]">{c.name}</span>
                </div>
                <span className="font-semibold text-slate-800">{c.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Two Column Tables: Recent Sales & Recent Movements */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Sales */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-serif font-bold text-slate-800 text-base">Latest Sales Orders</h3>
            <span className="text-xs text-slate-400">Database Real-time</span>
          </div>
          <div className="divide-y divide-slate-100">
            {recent_sales.length === 0 ? (
              <p className="p-6 text-xs text-slate-400 text-center">No sales recorded yet.</p>
            ) : (
              recent_sales.map((s) => (
                <div key={s.id} className="p-4 hover:bg-slate-50/50 flex items-center justify-between text-xs transition-colors">
                  <div>
                    <p className="font-semibold text-slate-800 font-mono">{s.so_number}</p>
                    <p className="text-slate-500 mt-0.5">{s.customer_name} • {s.date}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-slate-800">{formatCurrency(s.amount)}</p>
                    <div className="mt-1">
                      <Badge status={s.payment_status} />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Stock Movements */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-serif font-bold text-slate-800 text-base">Stock Movement Ledger</h3>
            <span className="text-xs text-slate-400">Audit Trail</span>
          </div>
          <div className="divide-y divide-slate-100">
            {recent_movements.length === 0 ? (
              <p className="p-6 text-xs text-slate-400 text-center">No stock movements recorded yet.</p>
            ) : (
              recent_movements.map((m) => (
                <div key={m.id} className="p-4 hover:bg-slate-50/50 flex items-center justify-between text-xs transition-colors">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-slate-700 font-semibold">{m.movement_number}</span>
                      <Badge status={m.movement_type} />
                    </div>
                    <p className="text-slate-500 mt-1 truncate max-w-xs">{m.reason}</p>
                  </div>
                  <div className="text-right">
                    <span className={`font-bold px-2 py-0.5 rounded text-xs ${
                      m.qty_change > 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                    }`}>
                      {m.qty_change > 0 ? `+${m.qty_change}` : m.qty_change}
                    </span>
                    <p className="text-[10px] text-slate-400 mt-1">{m.date}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
