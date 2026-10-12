import React, { useState, useEffect } from 'react';
import { CircleDot, Plus, Search } from 'lucide-react';
import api from '../api/client';
import type { Gemstone, Location, Supplier } from '../types';
import { formatCurrency, formatCarat } from '../utils/formatters';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';

export const GemstonesView: React.FC = () => {
  const { isInventoryManager } = useAuth();
  const [gemstones, setGemstones] = useState<Gemstone[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);

  const [newGem, setNewGem] = useState({
    sku: '',
    gemstone_type: 'Ruby',
    variety: '',
    is_natural: true,
    carat_weight: '',
    shape: 'Oval',
    color: 'Red',
    clarity: 'Eye Clean',
    cut: 'Faceted',
    treatment: 'None',
    certificate_lab: 'GIA',
    certificate_number: '',
    purchase_cost: '',
    selling_price: '',
    location_id: '',
    supplier_id: '',
    notes: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [gRes, lRes, sRes] = await Promise.all([
        api.get('/gemstones', { params: { query: search } }),
        api.get('/inventory/locations'),
        api.get('/parties/suppliers')
      ]);
      setGemstones(gRes.data.items);
      setLocations(lRes.data);
      setSuppliers(sRes.data);
      if (lRes.data.length > 0 && !newGem.location_id) {
        setNewGem(prev => ({ ...prev, location_id: lRes.data[0].id }));
      }
      if (sRes.data.length > 0 && !newGem.supplier_id) {
        setNewGem(prev => ({ ...prev, supplier_id: sRes.data[0].id }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/gemstones', {
        ...newGem,
        carat_weight: parseFloat(newGem.carat_weight),
        purchase_cost: parseFloat(newGem.purchase_cost),
        selling_price: parseFloat(newGem.selling_price)
      });
      setIsAddOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add gemstone');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div className="relative w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search stone type or variety..."
            className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
          />
        </div>

        {isInventoryManager && (
          <button
            onClick={() => setIsAddOpen(true)}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            Add Loose Gemstone
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">SKU #</th>
                <th className="py-3.5 px-4">Gemstone Type</th>
                <th className="py-3.5 px-4">Variety / Origin</th>
                <th className="py-3.5 px-4">Shape & Cut</th>
                <th className="py-3.5 px-4">Carat Weight</th>
                <th className="py-3.5 px-4">Color & Clarity</th>
                <th className="py-3.5 px-4">Treatment</th>
                <th className="py-3.5 px-4 text-right">Cost Price</th>
                <th className="py-3.5 px-4 text-right">Selling Price</th>
                <th className="py-3.5 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {gemstones.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    No loose gemstones in vault stock.
                  </td>
                </tr>
              ) : (
                gemstones.map((g) => (
                  <tr key={g.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{g.sku}</td>
                    <td className="py-3.5 px-4 font-bold text-slate-800">{g.gemstone_type}</td>
                    <td className="py-3.5 px-4">{g.variety || '-'}</td>
                    <td className="py-3.5 px-4">{g.shape}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">{formatCarat(g.carat_weight)}</td>
                    <td className="py-3.5 px-4">{g.color} • {g.clarity || '-'}</td>
                    <td className="py-3.5 px-4 text-slate-500">{g.treatment || 'None'}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(g.purchase_cost)}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">{formatCurrency(g.selling_price)}</td>
                    <td className="py-3.5 px-4 text-center">
                      <Badge status={g.status} />
                    </td>
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
        title="Register Loose Gemstone"
        maxWidth="2xl"
      >
        <form onSubmit={handleAddSubmit} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">SKU # *</label>
              <input
                type="text"
                required
                value={newGem.sku}
                onChange={(e) => setNewGem({ ...newGem, sku: e.target.value })}
                placeholder="GEM-2026-003"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Gemstone Type *</label>
              <select
                value={newGem.gemstone_type}
                onChange={(e) => setNewGem({ ...newGem, gemstone_type: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="Ruby">Ruby</option>
                <option value="Emerald">Emerald</option>
                <option value="Blue Sapphire">Blue Sapphire</option>
                <option value="Yellow Sapphire">Yellow Sapphire</option>
                <option value="Tanzanite">Tanzanite</option>
                <option value="Pearl">Pearl</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Carat Weight *</label>
              <input
                type="number"
                step="0.001"
                required
                value={newGem.carat_weight}
                onChange={(e) => setNewGem({ ...newGem, carat_weight: e.target.value })}
                placeholder="2.500"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Shape</label>
              <input
                type="text"
                value={newGem.shape}
                onChange={(e) => setNewGem({ ...newGem, shape: e.target.value })}
                placeholder="Oval, Cushion"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Color</label>
              <input
                type="text"
                value={newGem.color}
                onChange={(e) => setNewGem({ ...newGem, color: e.target.value })}
                placeholder="Vivid Blue, Deep Green"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Purchase Cost (INR) *</label>
              <input
                type="number"
                required
                value={newGem.purchase_cost}
                onChange={(e) => setNewGem({ ...newGem, purchase_cost: e.target.value })}
                placeholder="150000"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Asking Price (INR) *</label>
              <input
                type="number"
                required
                value={newGem.selling_price}
                onChange={(e) => setNewGem({ ...newGem, selling_price: e.target.value })}
                placeholder="220000"
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
              Save Gemstone
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
