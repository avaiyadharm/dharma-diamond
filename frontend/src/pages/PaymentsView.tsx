import React, { useState, useEffect } from 'react';
import { CreditCard, Plus } from 'lucide-react';
import api from '../api/client';
import type { Payment, Invoice } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';

export const PaymentsView: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddOpen, setIsAddOpen] = useState(false);

  const [newPayment, setNewPayment] = useState({
    invoice_id: '',
    amount: '',
    payment_method: 'Bank Transfer',
    reference_number: '',
    notes: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pRes, iRes] = await Promise.all([
        api.get('/payments'),
        api.get('/invoices')
      ]);
      setPayments(pRes.data.items);
      const unpaid = iRes.data.items.filter((i: Invoice) => i.balance_due > 0);
      setInvoices(unpaid);
      if (unpaid.length > 0 && !newPayment.invoice_id) {
        setNewPayment(prev => ({
          ...prev,
          invoice_id: unpaid[0].id,
          amount: unpaid[0].balance_due.toString()
        }));
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

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/payments', {
        payment_type: 'CUSTOMER_PAYMENT',
        invoice_id: newPayment.invoice_id,
        amount: parseFloat(newPayment.amount),
        payment_method: newPayment.payment_method,
        reference_number: newPayment.reference_number,
        notes: newPayment.notes
      });
      setIsAddOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Payment recording failed');
    }
  };

  const selectedInv = invoices.find(i => i.id === newPayment.invoice_id);

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h3 className="font-serif font-bold text-slate-800 text-base">Payment Receipts & Allocations</h3>
          <p className="text-xs text-slate-500">Record customer collections and supplier disbursements against commercial documents</p>
        </div>

        <button
          onClick={() => setIsAddOpen(true)}
          disabled={invoices.length === 0}
          className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          Record Customer Payment
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">Receipt #</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Type</th>
                <th className="py-3.5 px-4">Invoice / Ref</th>
                <th className="py-3.5 px-4">Customer / Supplier</th>
                <th className="py-3.5 px-4">Payment Method</th>
                <th className="py-3.5 px-4">Reference #</th>
                <th className="py-3.5 px-4 text-right">Amount</th>
                <th className="py-3.5 px-4">Recorded By</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {payments.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    No payment receipts logged yet.
                  </td>
                </tr>
              ) : (
                payments.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{p.payment_number}</td>
                    <td className="py-3.5 px-4">{formatDate(p.payment_date)}</td>
                    <td className="py-3.5 px-4">
                      <Badge status={p.payment_type} />
                    </td>
                    <td className="py-3.5 px-4 font-mono font-medium">{p.invoice_number || p.po_number || '-'}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">{p.customer_name || p.supplier_name || '-'}</td>
                    <td className="py-3.5 px-4 font-medium">{p.payment_method}</td>
                    <td className="py-3.5 px-4 font-mono text-slate-500">{p.reference_number || '-'}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-emerald-700 text-sm">{formatCurrency(p.amount)}</td>
                    <td className="py-3.5 px-4 text-slate-500">{p.recorder_name || 'Staff'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Record Customer Payment Receipt"
        maxWidth="md"
      >
        <form onSubmit={handleRecordPayment} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-700 mb-1">Select Outstanding Invoice *</label>
            <select
              value={newPayment.invoice_id}
              onChange={(e) => {
                const invId = e.target.value;
                const match = invoices.find(i => i.id === invId);
                setNewPayment({
                  ...newPayment,
                  invoice_id: invId,
                  amount: match ? match.balance_due.toString() : ''
                });
              }}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
            >
              {invoices.map((inv) => (
                <option key={inv.id} value={inv.id}>
                  {inv.invoice_number} • {inv.customer_name} (Due: {formatCurrency(inv.balance_due)})
                </option>
              ))}
            </select>
          </div>

          {selectedInv && (
            <div className="p-3 bg-amber-50/60 border border-amber-200 rounded-xl flex items-center justify-between">
              <div>
                <p className="text-[10px] text-amber-800 uppercase font-semibold">Total Invoice Amount</p>
                <p className="font-mono font-bold text-slate-900">{formatCurrency(selectedInv.grand_total)}</p>
              </div>
              <div className="text-right">
                <p className="text-[10px] text-amber-800 uppercase font-semibold">Balance Outstanding</p>
                <p className="font-mono font-bold text-rose-700">{formatCurrency(selectedInv.balance_due)}</p>
              </div>
            </div>
          )}

          <div>
            <label className="block font-medium text-slate-700 mb-1">Payment Amount (INR) *</label>
            <input
              type="number"
              step="0.01"
              required
              value={newPayment.amount}
              onChange={(e) => setNewPayment({ ...newPayment, amount: e.target.value })}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono font-bold"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Payment Method</label>
              <select
                value={newPayment.payment_method}
                onChange={(e) => setNewPayment({ ...newPayment, payment_method: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="Bank Transfer">Bank Transfer (NEFT/RTGS)</option>
                <option value="UPI">UPI</option>
                <option value="Card">Card</option>
                <option value="Cash">Cash</option>
                <option value="Cheque">Cheque</option>
              </select>
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Reference / UTR #</label>
              <input
                type="text"
                value={newPayment.reference_number}
                onChange={(e) => setNewPayment({ ...newPayment, reference_number: e.target.value })}
                placeholder="UTR-2026-90214"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
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
              Confirm Payment
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
