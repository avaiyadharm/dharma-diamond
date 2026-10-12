import React, { useState, useEffect } from 'react';
import { ArrowLeftRight, Search, ShieldCheck } from 'lucide-react';
import api from '../api/client';
import type { StockMovement } from '../types';
import { formatCarat, formatWeightGrams, formatDate } from '../utils/formatters';
import { Badge } from '../components/common/Badge';

export const StockMovementsView: React.FC = () => {
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState('');

  const fetchMovements = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (selectedType) params.movement_type = selectedType;
      const res = await api.get('/inventory/movements', { params });
      setMovements(res.data.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovements();
  }, [selectedType]);

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h3 className="font-serif font-bold text-slate-800 text-base">Immutable Stock Movement Ledger</h3>
          <p className="text-xs text-slate-500">Every vault inventory fluctuation is auditable, chronological, and cannot be modified</p>
        </div>

        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
        >
          <option value="">All Movement Types</option>
          <option value="OPENING_STOCK">Opening Stock</option>
          <option value="PURCHASE_RECEIPT">Purchase Receipt</option>
          <option value="SALE">Sale Checkout</option>
          <option value="CUSTOMER_RETURN">Customer Return / Reversal</option>
          <option value="LOCATION_TRANSFER">Location Transfer</option>
          <option value="STOCK_ADJUSTMENT">Stock Adjustment</option>
          <option value="MOUNTED_IN_JEWELLERY">Mounted in Jewellery</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">Movement #</th>
                <th className="py-3.5 px-4">Date & Time</th>
                <th className="py-3.5 px-4">Type</th>
                <th className="py-3.5 px-4">Item SKU / Ref</th>
                <th className="py-3.5 px-4 text-center">Qty Change</th>
                <th className="py-3.5 px-4">Weight / Carats</th>
                <th className="py-3.5 px-4">Source Location</th>
                <th className="py-3.5 px-4">Destination</th>
                <th className="py-3.5 px-4">Authorized User</th>
                <th className="py-3.5 px-4">Reason / Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {movements.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    No movement records found.
                  </td>
                </tr>
              ) : (
                movements.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{m.movement_number}</td>
                    <td className="py-3.5 px-4">{formatDate(m.created_at)}</td>
                    <td className="py-3.5 px-4">
                      <Badge status={m.movement_type} />
                    </td>
                    <td className="py-3.5 px-4 font-mono font-semibold text-amber-800">{m.item_sku || '-'}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded font-bold ${
                        m.qty_change > 0
                          ? 'bg-emerald-50 text-emerald-700'
                          : m.qty_change < 0
                          ? 'bg-rose-50 text-rose-700'
                          : 'bg-slate-100 text-slate-700'
                      }`}>
                        {m.qty_change > 0 ? `+${m.qty_change}` : m.qty_change}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono">
                      {m.carat_change ? formatCarat(m.carat_change) : m.weight_change_grams ? formatWeightGrams(m.weight_change_grams) : '-'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">{m.source_location_name || '-'}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">{m.destination_location_name || '-'}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-700">{m.user_name || 'System'}</td>
                    <td className="py-3.5 px-4 text-slate-500 truncate max-w-xs">{m.reason || '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
