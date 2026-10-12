import React, { useState, useEffect } from 'react';
import { BarChart3, Download, FileSpreadsheet, TrendingUp, ShieldAlert } from 'lucide-react';
import api from '../api/client';
import { formatCurrency } from '../utils/formatters';

export const ReportsView: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const res = await api.get('/dashboard');
        setMetrics(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  const handleDownloadCSV = (endpoint: string, filename: string) => {
    const token = localStorage.getItem('dharma_token');
    fetch(`/api/v1/reports/export/${endpoint}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch(() => alert('Failed to download CSV'));
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h3 className="font-serif font-bold text-slate-800 text-base">Business Intelligence & Exportable Reports</h3>
          <p className="text-xs text-slate-500">Valuation audit, COGS profitability, and Excel-compatible data exports</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleDownloadCSV('diamonds.csv', 'Dharma_Diamonds_Inventory.csv')}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            Export Diamonds CSV
          </button>
          <button
            onClick={() => handleDownloadCSV('sales.csv', 'Dharma_Sales_Ledger.csv')}
            className="px-3.5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4 text-amber-200" />
            Export Sales CSV
          </button>
        </div>
      </div>

      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
            <h4 className="font-serif font-bold text-slate-800 text-base">Stock Valuation Summary</h4>
            <div className="space-y-2 text-xs pt-2">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Inventory Cost Value:</span>
                <span className="font-mono font-bold text-slate-800">{formatCurrency(metrics.inventory.total_cost_valuation)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Estimated Retail Asking Value:</span>
                <span className="font-mono font-bold text-emerald-700">{formatCurrency(metrics.inventory.total_asking_valuation)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Unrealized Inventory Margin:</span>
                <span className="font-mono font-bold text-amber-700">
                  {formatCurrency(metrics.inventory.total_asking_valuation - metrics.inventory.total_cost_valuation)}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
            <h4 className="font-serif font-bold text-slate-800 text-base">Profitability & Margin</h4>
            <div className="space-y-2 text-xs pt-2">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Revenue Month-to-Date:</span>
                <span className="font-mono font-bold text-slate-800">{formatCurrency(metrics.business.sales_revenue_month)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Gross Profit on Closed Sales:</span>
                <span className="font-mono font-bold text-emerald-700">{formatCurrency(metrics.business.gross_profit_month)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Gross Profit Margin:</span>
                <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  {metrics.business.gross_margin_pct}%
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
            <h4 className="font-serif font-bold text-slate-800 text-base">Working Capital & Credit</h4>
            <div className="space-y-2 text-xs pt-2">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Customer Receivables:</span>
                <span className="font-mono font-bold text-amber-700">{formatCurrency(metrics.business.outstanding_receivables)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Supplier Payables:</span>
                <span className="font-mono font-bold text-rose-700">{formatCurrency(metrics.business.outstanding_payables)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Net Operational Balance:</span>
                <span className="font-mono font-bold text-slate-900">
                  {formatCurrency(metrics.business.outstanding_receivables - metrics.business.outstanding_payables)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
