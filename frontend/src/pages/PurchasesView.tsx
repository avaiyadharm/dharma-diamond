import React, { useState, useEffect } from 'react';
import { ShoppingBag, Plus, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../api/client';
import type { PurchaseOrder, Supplier, Location } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';

export const PurchasesView: React.FC = () => {
  const { isInventoryManager } = useAuth();
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [isReceiveOpen, setIsReceiveOpen] = useState(false);
  const [receiveLocationId, setReceiveLocationId] = useState('');
  const [receiveNotes, setReceiveNotes] = useState('');

  // PO form state
  const [newPO, setNewPO] = useState({
    supplier_id: '',
    notes: '',
    tax_rate_pct: 3.0,
    items: [
      {
        item_type: 'DIAMOND',
        description: 'Polished Solitaire Diamonds Lot',
        quantity: 2,
        carat_weight: 3.0,
        unit_price: 250000,
        line_total: 500000
      }
    ]
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pRes, sRes, lRes] = await Promise.all([
        api.get('/purchases'),
        api.get('/parties/suppliers'),
        api.get('/inventory/locations')
      ]);
      setOrders(pRes.data.items);
      setSuppliers(sRes.data);
      setLocations(lRes.data);
      if (sRes.data.length > 0 && !newPO.supplier_id) {
        setNewPO(prev => ({ ...prev, supplier_id: sRes.data[0].id }));
      }
      if (lRes.data.length > 0) {
        setReceiveLocationId(lRes.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreatePO = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/purchases', newPO);
      setIsAddOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create purchase order');
    }
  };

  const handleConfirmReceipt = async () => {
    if (!selectedPO) return;
    try {
      await api.post('/purchases/receive', {
        purchase_order_id: selectedPO.id,
        location_id: receiveLocationId,
        notes: receiveNotes
      });
      setIsReceiveOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to confirm receipt');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h3 className="font-serif font-bold text-slate-800 text-base">Purchase Orders & Inward Receiving</h3>
          <p className="text-xs text-slate-500">Track vendor shipments, weight verification, and goods receipt notes</p>
        </div>

        {isInventoryManager && (
          <button
            onClick={() => setIsAddOpen(true)}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            Create Purchase Order
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">PO Number</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Supplier</th>
                <th className="py-3.5 px-4 text-right">Subtotal</th>
                <th className="py-3.5 px-4 text-right">GST (3%)</th>
                <th className="py-3.5 px-4 text-right">Grand Total</th>
                <th className="py-3.5 px-4 text-right">Amount Paid</th>
                <th className="py-3.5 px-4 text-center">Status</th>
                <th className="py-3.5 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {orders.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    No purchase orders recorded.
                  </td>
                </tr>
              ) : (
                orders.map((po) => (
                  <tr key={po.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{po.po_number}</td>
                    <td className="py-3.5 px-4">{formatDate(po.purchase_date)}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">{po.supplier_name}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(po.subtotal)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(po.tax_amount)}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">{formatCurrency(po.total_amount)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-700">{formatCurrency(po.amount_paid)}</td>
                    <td className="py-3.5 px-4 text-center">
                      <Badge status={po.status} />
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {po.status === 'CONFIRMED' && isInventoryManager && (
                        <button
                          onClick={() => {
                            setSelectedPO(po);
                            setIsReceiveOpen(true);
                          }}
                          className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-xs font-semibold hover:bg-emerald-100 transition-colors"
                        >
                          Receive Goods
                        </button>
                      )}
                      {po.status === 'RECEIVED' && (
                        <span className="text-emerald-600 font-semibold flex items-center justify-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Received
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Confirm Receipt Modal */}
      {selectedPO && (
        <Modal
          isOpen={isReceiveOpen}
          onClose={() => setIsReceiveOpen(false)}
          title={`Confirm Goods Receipt: ${selectedPO.po_number}`}
          maxWidth="md"
        >
          <div className="space-y-4 text-xs">
            <p className="text-slate-600">
              Confirming receipt will verify physical scale weights and automatically increase vault stock with an immutable PURCHASE_RECEIPT ledger entry.
            </p>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Store into Vault Location</label>
              <select
                value={receiveLocationId}
                onChange={(e) => setReceiveLocationId(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>{loc.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Inspection & Verification Notes</label>
              <input
                type="text"
                value={receiveNotes}
                onChange={(e) => setReceiveNotes(e.target.value)}
                placeholder="Scale weights verified against packaging slips"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>

            <div className="pt-3 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsReceiveOpen(false)}
                className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmReceipt}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold"
              >
                Confirm Goods Inward
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Create PO Modal */}
      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Draft Supplier Purchase Order"
        maxWidth="2xl"
      >
        <form onSubmit={handleCreatePO} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-700 mb-1">Select Supplier *</label>
            <select
              value={newPO.supplier_id}
              onChange={(e) => setNewPO({ ...newPO, supplier_id: e.target.value })}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            >
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>{s.business_name} ({s.category})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">Item Description *</label>
            <input
              type="text"
              required
              value={newPO.items[0].description}
              onChange={(e) => {
                const updated = [...newPO.items];
                updated[0].description = e.target.value;
                setNewPO({ ...newPO, items: updated });
              }}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Quantity</label>
              <input
                type="number"
                value={newPO.items[0].quantity}
                onChange={(e) => {
                  const qty = parseInt(e.target.value) || 1;
                  const updated = [...newPO.items];
                  updated[0].quantity = qty;
                  updated[0].line_total = qty * updated[0].unit_price;
                  setNewPO({ ...newPO, items: updated });
                }}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Unit Price (INR)</label>
              <input
                type="number"
                value={newPO.items[0].unit_price}
                onChange={(e) => {
                  const price = parseFloat(e.target.value) || 0;
                  const updated = [...newPO.items];
                  updated[0].unit_price = price;
                  updated[0].line_total = price * updated[0].quantity;
                  setNewPO({ ...newPO, items: updated });
                }}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Total (INR)</label>
              <input
                type="text"
                disabled
                value={formatCurrency(newPO.items[0].line_total)}
                className="w-full p-2.5 bg-slate-100 border border-slate-200 rounded-lg font-mono font-bold"
              />
            </div>
          </div>

          <div className="pt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAddOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold"
            >
              Confirm Purchase Order
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
