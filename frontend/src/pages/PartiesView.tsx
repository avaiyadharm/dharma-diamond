import React, { useState, useEffect } from 'react';
import { Users, Plus, Building, Phone, Mail, MapPin } from 'lucide-react';
import api from '../api/client';
import type { Supplier, Customer } from '../types';
import { Modal } from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';

export const PartiesView: React.FC = () => {
  const { isInventoryManager, isSalesStaff } = useAuth();
  const [activeTab, setActiveTab] = useState<'suppliers' | 'customers'>('suppliers');
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  const [isAddSupplierOpen, setIsAddSupplierOpen] = useState(false);
  const [isAddCustomerOpen, setIsAddCustomerOpen] = useState(false);

  const [newSupplier, setNewSupplier] = useState({
    business_name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    tax_id: '',
    category: 'Rough & Polished Diamonds',
    payment_terms: 'Net 30 Days'
  });

  const [newCustomer, setNewCustomer] = useState({
    name: '',
    company_name: '',
    phone: '',
    email: '',
    billing_address: '',
    tax_id: '',
    customer_type: 'Retail'
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sRes, cRes] = await Promise.all([
        api.get('/parties/suppliers'),
        api.get('/parties/customers')
      ]);
      setSuppliers(sRes.data);
      setCustomers(cRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/parties/suppliers', newSupplier);
      setIsAddSupplierOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add supplier');
    }
  };

  const handleAddCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/parties/customers', newCustomer);
      setIsAddCustomerOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add customer');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('suppliers')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'suppliers'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Suppliers & Bourses ({suppliers.length})
          </button>
          <button
            onClick={() => setActiveTab('customers')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'customers'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Customers & Retail Clients ({customers.length})
          </button>
        </div>

        {activeTab === 'suppliers' && isInventoryManager && (
          <button
            onClick={() => setIsAddSupplierOpen(true)}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            Add Supplier
          </button>
        )}

        {activeTab === 'customers' && isSalesStaff && (
          <button
            onClick={() => setIsAddCustomerOpen(true)}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            Add Customer
          </button>
        )}
      </div>

      {/* Suppliers Tab */}
      {activeTab === 'suppliers' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {suppliers.map((s) => (
            <div key={s.id} className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  {s.category}
                </span>
                <span className="text-xs text-slate-400 font-mono">{s.payment_terms || 'Net 30'}</span>
              </div>
              <h4 className="font-serif font-bold text-slate-800 text-base">{s.business_name}</h4>
              <div className="space-y-1.5 text-xs text-slate-500 pt-1">
                {s.contact_person && <p className="text-slate-700 font-medium">Contact: {s.contact_person}</p>}
                {s.phone && <p className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5 text-slate-400" /> {s.phone}</p>}
                {s.email && <p className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5 text-slate-400" /> {s.email}</p>}
                {s.tax_id && <p className="font-mono text-[11px] text-slate-600">GSTIN: {s.tax_id}</p>}
                {s.address && <p className="text-slate-400 text-[11px] truncate">{s.address}</p>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Customers Tab */}
      {activeTab === 'customers' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {customers.map((c) => (
            <div key={c.id} className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  {c.customer_type}
                </span>
                {c.tax_id && <span className="text-[11px] font-mono text-slate-500">GSTIN: {c.tax_id}</span>}
              </div>
              <div>
                <h4 className="font-serif font-bold text-slate-800 text-base">{c.name}</h4>
                {c.company_name && <p className="text-xs text-slate-500 font-medium">{c.company_name}</p>}
              </div>
              <div className="space-y-1.5 text-xs text-slate-500 pt-1">
                {c.phone && <p className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5 text-slate-400" /> {c.phone}</p>}
                {c.email && <p className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5 text-slate-400" /> {c.email}</p>}
                {c.billing_address && <p className="text-slate-400 text-[11px] line-clamp-2">{c.billing_address}</p>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Supplier Modal */}
      <Modal
        isOpen={isAddSupplierOpen}
        onClose={() => setIsAddSupplierOpen(false)}
        title="Add Vendor / Diamond Supplier"
        maxWidth="md"
      >
        <form onSubmit={handleAddSupplier} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-700 mb-1">Business Name *</label>
            <input
              type="text"
              required
              value={newSupplier.business_name}
              onChange={(e) => setNewSupplier({ ...newSupplier, business_name: e.target.value })}
              placeholder="Surat Diamond Bourse Exports"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Contact Person</label>
              <input
                type="text"
                value={newSupplier.contact_person}
                onChange={(e) => setNewSupplier({ ...newSupplier, contact_person: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Phone</label>
              <input
                type="text"
                value={newSupplier.phone}
                onChange={(e) => setNewSupplier({ ...newSupplier, phone: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
          </div>
          <div>
            <label className="block font-medium text-slate-700 mb-1">GSTIN / Tax ID</label>
            <input
              type="text"
              value={newSupplier.tax_id}
              onChange={(e) => setNewSupplier({ ...newSupplier, tax_id: e.target.value })}
              placeholder="24AAACS1234F1Z5"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
            />
          </div>
          <div>
            <label className="block font-medium text-slate-700 mb-1">Address</label>
            <textarea
              rows={2}
              value={newSupplier.address}
              onChange={(e) => setNewSupplier({ ...newSupplier, address: e.target.value })}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="pt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAddSupplierOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold"
            >
              Save Supplier
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Customer Modal */}
      <Modal
        isOpen={isAddCustomerOpen}
        onClose={() => setIsAddCustomerOpen(false)}
        title="Add Customer Account"
        maxWidth="md"
      >
        <form onSubmit={handleAddCustomer} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-700 mb-1">Customer Full Name *</label>
            <input
              type="text"
              required
              value={newCustomer.name}
              onChange={(e) => setNewCustomer({ ...newCustomer, name: e.target.value })}
              placeholder="Vikramaditya Roy"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Company (Optional)</label>
              <input
                type="text"
                value={newCustomer.company_name}
                onChange={(e) => setNewCustomer({ ...newCustomer, company_name: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Customer Type</label>
              <select
                value={newCustomer.customer_type}
                onChange={(e) => setNewCustomer({ ...newCustomer, customer_type: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="Retail">Retail HNW Client</option>
                <option value="Wholesale">Wholesale Jeweller</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Phone Number</label>
              <input
                type="text"
                value={newCustomer.phone}
                onChange={(e) => setNewCustomer({ ...newCustomer, phone: e.target.value })}
                placeholder="+91 98200 12345"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Email</label>
              <input
                type="email"
                value={newCustomer.email}
                onChange={(e) => setNewCustomer({ ...newCustomer, email: e.target.value })}
                placeholder="client@gmail.com"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
          </div>
          <div>
            <label className="block font-medium text-slate-700 mb-1">Billing Address</label>
            <textarea
              rows={2}
              value={newCustomer.billing_address}
              onChange={(e) => setNewCustomer({ ...newCustomer, billing_address: e.target.value })}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="pt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAddCustomerOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold"
            >
              Register Customer
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
