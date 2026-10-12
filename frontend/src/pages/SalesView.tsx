import React, { useState, useEffect } from 'react';
import { ShoppingCart, Plus, CheckCircle, XCircle, Search, Eye } from 'lucide-react';
import api from '../api/client';
import type { SalesOrder, Customer, Diamond, JewelleryItem } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';

export const SalesView: React.FC = () => {
  const { isSalesStaff, isAdmin } = useAuth();
  const [sales, setSales] = useState<SalesOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [availableDiamonds, setAvailableDiamonds] = useState<Diamond[]>([]);
  const [availableJewellery, setAvailableJewellery] = useState<JewelleryItem[]>([]);

  const [isNewSaleOpen, setIsNewSaleOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);

  // New Sale Form
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [itemType, setItemType] = useState<'DIAMOND' | 'JEWELLERY'>('DIAMOND');
  const [selectedItemId, setSelectedItemId] = useState('');
  const [discountAmount, setDiscountAmount] = useState('0.00');
  const [initialPayment, setInitialPayment] = useState('0.00');
  const [paymentMethod, setPaymentMethod] = useState('Bank Transfer');
  const [saleNotes, setSaleNotes] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sRes, cRes, dRes, jRes] = await Promise.all([
        api.get('/sales'),
        api.get('/parties/customers'),
        api.get('/diamonds', { params: { status: 'AVAILABLE' } }),
        api.get('/jewellery/items', { params: { status: 'AVAILABLE' } })
      ]);
      setSales(sRes.data.items);
      setCustomers(cRes.data);
      setAvailableDiamonds(dRes.data.items);
      setAvailableJewellery(jRes.data.items);

      if (cRes.data.length > 0 && !selectedCustomerId) {
        setSelectedCustomerId(cRes.data[0].id);
      }
      if (dRes.data.items.length > 0 && !selectedItemId) {
        setSelectedItemId(dRes.data.items[0].id);
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

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    let selectedItemObj: any = null;
    if (itemType === 'DIAMOND') {
      selectedItemObj = availableDiamonds.find(d => d.id === selectedItemId);
    } else {
      selectedItemObj = availableJewellery.find(j => j.id === selectedItemId);
    }

    if (!selectedItemObj) {
      setErrorMsg('Please select an item to sell.');
      return;
    }

    try {
      await api.post('/sales', {
        customer_id: selectedCustomerId,
        tax_rate_pct: 3.0,
        discount_amount: parseFloat(discountAmount) || 0,
        initial_payment_amount: parseFloat(initialPayment) || 0,
        payment_method: paymentMethod,
        notes: saleNotes,
        items: [
          {
            item_type: itemType,
            diamond_id: itemType === 'DIAMOND' ? selectedItemObj.id : undefined,
            jewellery_item_id: itemType === 'JEWELLERY' ? selectedItemObj.id : undefined,
            sku: selectedItemObj.sku,
            description: itemType === 'DIAMOND'
              ? `${selectedItemObj.carat_weight}ct ${selectedItemObj.shape} Diamond (${selectedItemObj.color_grade}/${selectedItemObj.clarity_grade})`
              : `${selectedItemObj.product_name} (${selectedItemObj.purity} ${selectedItemObj.metal_type})`,
            quantity: 1,
            unit_price: selectedItemObj.asking_price || selectedItemObj.selling_price,
            discount: 0
          }
        ]
      });

      setIsNewSaleOpen(false);
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Sales checkout failed');
    }
  };

  const handleCancelSale = async (orderId: string) => {
    const reason = prompt('Please enter the reason for cancelling this sale:');
    if (!reason) return;
    try {
      await api.post(`/sales/${orderId}/cancel`, { reason });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Cancellation failed');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h3 className="font-serif font-bold text-slate-800 text-base">Sales Orders & Commercial Invoicing</h3>
          <p className="text-xs text-slate-500">Atomic inventory deduction, COGS snapshotting, and automatic GST invoice generation</p>
        </div>

        {isSalesStaff && (
          <button
            onClick={() => setIsNewSaleOpen(true)}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm"
          >
            <Plus className="w-4 h-4" />
            New Sales Order
          </button>
        )}
      </div>

      {/* Sales Orders Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">SO #</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Customer</th>
                <th className="py-3.5 px-4 text-right">Subtotal</th>
                <th className="py-3.5 px-4 text-right">GST (3%)</th>
                <th className="py-3.5 px-4 text-right">Final Amount</th>
                <th className="py-3.5 px-4 text-right">Amount Paid</th>
                <th className="py-3.5 px-4 text-center">Payment Status</th>
                <th className="py-3.5 px-4 text-center">Status</th>
                <th className="py-3.5 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {sales.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    No sales orders recorded yet.
                  </td>
                </tr>
              ) : (
                sales.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{s.so_number}</td>
                    <td className="py-3.5 px-4">{formatDate(s.sales_date)}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">{s.customer_name || 'Counter Customer'}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(s.subtotal)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(s.tax_amount)}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">{formatCurrency(s.total_amount)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-emerald-700 font-semibold">{formatCurrency(s.amount_paid)}</td>
                    <td className="py-3.5 px-4 text-center">
                      <Badge status={s.payment_status} />
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <Badge status={s.status} />
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        <button
                          onClick={() => setSelectedOrder(s)}
                          title="View Order Items"
                          className="p-1 text-slate-500 hover:text-amber-600 rounded"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {s.status === 'CONFIRMED' && isAdmin && (
                          <button
                            onClick={() => handleCancelSale(s.id)}
                            title="Cancel Sale & Reverse Stock"
                            className="p-1 text-rose-500 hover:text-rose-700 rounded"
                          >
                            <XCircle className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* View Order Modal */}
      {selectedOrder && (
        <Modal
          isOpen={!!selectedOrder}
          onClose={() => setSelectedOrder(null)}
          title={`Order Breakdown: ${selectedOrder.so_number}`}
        >
          <div className="space-y-4 text-xs">
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
              <div>
                <p className="font-semibold text-slate-800">{selectedOrder.customer_name}</p>
                <p className="text-slate-500">Salesperson: {selectedOrder.salesperson_name || 'Staff'}</p>
              </div>
              <div className="text-right">
                <p className="font-mono font-bold text-base text-slate-900">{formatCurrency(selectedOrder.total_amount)}</p>
                <Badge status={selectedOrder.status} />
              </div>
            </div>

            <div>
              <h4 className="font-serif font-bold text-slate-800 mb-2">Sold Items & Locked COGS</h4>
              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="p-2.5">SKU</th>
                      <th className="p-2.5">Description</th>
                      <th className="p-2.5 text-right">Historical Cost</th>
                      <th className="p-2.5 text-right">Selling Price</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {selectedOrder.items.map((it) => (
                      <tr key={it.id}>
                        <td className="p-2.5 font-mono font-semibold">{it.sku}</td>
                        <td className="p-2.5">{it.description}</td>
                        <td className="p-2.5 text-right font-mono text-slate-500">{formatCurrency(it.cost_price)}</td>
                        <td className="p-2.5 text-right font-mono font-bold">{formatCurrency(it.unit_price)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* New Sale Modal */}
      <Modal
        isOpen={isNewSaleOpen}
        onClose={() => setIsNewSaleOpen(false)}
        title="Finalize Sales Checkout"
        maxWidth="2xl"
      >
        <form onSubmit={handleCheckout} className="space-y-4 text-xs">
          {errorMsg && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl">
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block font-medium text-slate-700 mb-1">Customer *</label>
            <select
              value={selectedCustomerId}
              onChange={(e) => setSelectedCustomerId(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            >
              {customers.map((c) => (
                <option key={c.id} value={c.id}>{c.name} {c.company_name ? `(${c.company_name})` : ''}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Item Category</label>
              <select
                value={itemType}
                onChange={(e) => {
                  const val = e.target.value as 'DIAMOND' | 'JEWELLERY';
                  setItemType(val);
                  if (val === 'DIAMOND' && availableDiamonds.length > 0) {
                    setSelectedItemId(availableDiamonds[0].id);
                  } else if (val === 'JEWELLERY' && availableJewellery.length > 0) {
                    setSelectedItemId(availableJewellery[0].id);
                  }
                }}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="DIAMOND">Certified Solitaire Diamond</option>
                <option value="JEWELLERY">Finished Jewellery Piece</option>
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Select Available Item *</label>
              <select
                value={selectedItemId}
                onChange={(e) => setSelectedItemId(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                {itemType === 'DIAMOND'
                  ? availableDiamonds.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.sku} • {d.carat_weight}ct {d.shape} ({formatCurrency(d.asking_price)})
                      </option>
                    ))
                  : availableJewellery.map((j) => (
                      <option key={j.id} value={j.id}>
                        {j.sku} • {j.product_name} ({formatCurrency(j.selling_price)})
                      </option>
                    ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Negotiated Discount (INR)</label>
              <input
                type="number"
                value={discountAmount}
                onChange={(e) => setDiscountAmount(e.target.value)}
                placeholder="0.00"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Initial Payment Received (INR)</label>
              <input
                type="number"
                value={initialPayment}
                onChange={(e) => setInitialPayment(e.target.value)}
                placeholder="0.00"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Payment Method</label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="Bank Transfer">Bank Transfer (NEFT/RTGS)</option>
                <option value="UPI">UPI (GooglePay / PhonePe / Paytm)</option>
                <option value="Card">Credit / Debit Card</option>
                <option value="Cash">Cash Counter</option>
                <option value="Cheque">Cheque</option>
              </select>
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Sale Notes</label>
              <input
                type="text"
                value={saleNotes}
                onChange={(e) => setSaleNotes(e.target.value)}
                placeholder="Special occasion, ring sizing..."
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
          </div>

          <div className="pt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsNewSaleOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold shadow-sm"
            >
              Finalize Sale & Generate GST Invoice
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
