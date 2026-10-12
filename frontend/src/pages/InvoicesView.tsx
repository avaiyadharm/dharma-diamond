import React, { useState, useEffect } from 'react';
import { FileText, Download, Printer } from 'lucide-react';
import api from '../api/client';
import type { Invoice } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Badge } from '../components/common/Badge';

export const InvoicesView: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const res = await api.get('/invoices');
      setInvoices(res.data.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleDownloadPDF = async (invoiceId: string, invoiceNumber: string) => {
    try {
      const res = await api.get(`/invoices/${invoiceId}/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${invoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err) {
      alert('Failed to generate PDF document');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h3 className="font-serif font-bold text-slate-800 text-base">Tax Invoices (GST Compliant)</h3>
          <p className="text-xs text-slate-500">Official commercial invoices with itemized CGST & SGST breakdowns</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">Invoice #</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Billed To</th>
                <th className="py-3.5 px-4 text-right">Taxable Subtotal</th>
                <th className="py-3.5 px-4 text-right">CGST (1.5%)</th>
                <th className="py-3.5 px-4 text-right">SGST (1.5%)</th>
                <th className="py-3.5 px-4 text-right">Grand Total</th>
                <th className="py-3.5 px-4 text-right">Amount Paid</th>
                <th className="py-3.5 px-4 text-right">Balance Due</th>
                <th className="py-3.5 px-4 text-center">Status</th>
                <th className="py-3.5 px-4 text-center">Download PDF</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-slate-400">
                    No invoices generated yet.
                  </td>
                </tr>
              ) : (
                invoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{inv.invoice_number}</td>
                    <td className="py-3.5 px-4">{formatDate(inv.invoice_date)}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">{inv.customer_name}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(inv.subtotal)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(inv.cgst_amount)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(inv.sgst_amount)}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">{formatCurrency(inv.grand_total)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-emerald-700 font-semibold">{formatCurrency(inv.amount_paid)}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-rose-700">{formatCurrency(inv.balance_due)}</td>
                    <td className="py-3.5 px-4 text-center">
                      <Badge status={inv.status} />
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={() => handleDownloadPDF(inv.id, inv.invoice_number)}
                        className="px-2.5 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded text-xs font-semibold hover:bg-amber-100 flex items-center gap-1 mx-auto transition-colors"
                      >
                        <Printer className="w-3.5 h-3.5" /> PDF
                      </button>
                    </td>
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
