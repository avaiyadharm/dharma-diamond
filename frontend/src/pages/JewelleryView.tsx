import React, { useState, useEffect } from 'react';
import { Sparkles, Plus, Search, Eye, Layers, ShieldCheck, Scale } from 'lucide-react';
import api from '../api/client';
import type { JewelleryItem, JewelleryProduct, Location, Supplier } from '../types';
import { formatCurrency, formatWeightGrams, formatCarat } from '../utils/formatters';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';

export const JewelleryView: React.FC = () => {
  const { isInventoryManager } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState<'items' | 'designs'>('items');
  const [items, setItems] = useState<JewelleryItem[]>([]);
  const [designs, setDesigns] = useState<JewelleryProduct[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  // Modals
  const [isAddOpen, setIsAddOpen] = useState<boolean>(false);
  const [isAddDesignOpen, setIsAddDesignOpen] = useState<boolean>(false);
  const [selectedItem, setSelectedItem] = useState<JewelleryItem | null>(null);

  const [locations, setLocations] = useState<Location[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);

  // Add Item Form
  const [newItem, setNewItem] = useState({
    sku: '',
    product_id: '',
    gross_weight_grams: '',
    net_metal_weight_grams: '',
    hallmark_details: 'BIS 750 (18K)',
    metal_cost: '',
    stone_cost: '',
    making_charge: '',
    other_costs: '0.00',
    total_cost: '',
    selling_price: '',
    location_id: '',
    supplier_id: '',
    notes: ''
  });

  // Add Design Form
  const [newDesign, setNewDesign] = useState({
    design_code: '',
    name: '',
    category: 'Ring',
    collection: '',
    metal_type: 'Gold',
    purity: '18K',
    description: '',
    image_url: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [itemsRes, designsRes, locsRes, suppsRes] = await Promise.all([
        api.get('/jewellery/items', { params: { query: search, category: selectedCategory } }),
        api.get('/jewellery/products'),
        api.get('/inventory/locations'),
        api.get('/parties/suppliers')
      ]);
      setItems(itemsRes.data.items);
      setDesigns(designsRes.data.items);
      setLocations(locsRes.data);
      setSuppliers(suppsRes.data);

      if (designsRes.data.items.length > 0 && !newItem.product_id) {
        setNewItem(prev => ({ ...prev, product_id: designsRes.data.items[0].id }));
      }
      if (locsRes.data.length > 0 && !newItem.location_id) {
        setNewItem(prev => ({ ...prev, location_id: locsRes.data[0].id }));
      }
      if (suppsRes.data.length > 0 && !newItem.supplier_id) {
        setNewItem(prev => ({ ...prev, supplier_id: suppsRes.data[0].id }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search, selectedCategory]);

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const metalCost = parseFloat(newItem.metal_cost) || 0;
      const stoneCost = parseFloat(newItem.stone_cost) || 0;
      const making = parseFloat(newItem.making_charge) || 0;
      const other = parseFloat(newItem.other_costs) || 0;
      const totalCost = metalCost + stoneCost + making + other;

      await api.post('/jewellery/items', {
        ...newItem,
        gross_weight_grams: parseFloat(newItem.gross_weight_grams),
        net_metal_weight_grams: parseFloat(newItem.net_metal_weight_grams),
        metal_cost: metalCost,
        stone_cost: stoneCost,
        making_charge: making,
        other_costs: other,
        total_cost: totalCost,
        selling_price: parseFloat(newItem.selling_price),
      });
      setIsAddOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add jewellery piece');
    }
  };

  const handleAddDesign = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/jewellery/products', newDesign);
      setIsAddDesignOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create design product');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      {/* Top Header & Sub-Tabs */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveSubTab('items')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeSubTab === 'items'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Physical Inventory Pieces ({items.length})
          </button>
          <button
            onClick={() => setActiveSubTab('designs')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeSubTab === 'designs'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Master Design Catalog ({designs.length})
          </button>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-56">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search design or SKU..."
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
            />
          </div>

          {isInventoryManager && activeSubTab === 'items' && (
            <button
              onClick={() => setIsAddOpen(true)}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Finished Piece
            </button>
          )}

          {isInventoryManager && activeSubTab === 'designs' && (
            <button
              onClick={() => setIsAddDesignOpen(true)}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Design Template
            </button>
          )}
        </div>
      </div>

      {/* View 1: Physical Items Table */}
      {activeSubTab === 'items' && (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                  <th className="py-3.5 px-4">SKU / Item #</th>
                  <th className="py-3.5 px-4">Design Name</th>
                  <th className="py-3.5 px-4">Category</th>
                  <th className="py-3.5 px-4">Metal & Purity</th>
                  <th className="py-3.5 px-4 text-right">Gross Wt (g)</th>
                  <th className="py-3.5 px-4 text-right">Net Gold (g)</th>
                  <th className="py-3.5 px-4 text-right">Stones (ct)</th>
                  <th className="py-3.5 px-4 text-right">Total Cost</th>
                  <th className="py-3.5 px-4 text-right">Retail Price</th>
                  <th className="py-3.5 px-4 text-center">Status</th>
                  <th className="py-3.5 px-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {items.length === 0 ? (
                  <tr>
                    <td colSpan={11} className="py-12 text-center text-slate-400">
                      No jewellery pieces found.
                    </td>
                  </tr>
                ) : (
                  items.map((it) => (
                    <tr key={it.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{it.sku}</td>
                      <td className="py-3.5 px-4 font-medium text-slate-800">{it.product_name}</td>
                      <td className="py-3.5 px-4">{it.product_category}</td>
                      <td className="py-3.5 px-4 font-medium">{it.purity} {it.metal_type}</td>
                      <td className="py-3.5 px-4 text-right font-semibold text-slate-800">{formatWeightGrams(it.gross_weight_grams)}</td>
                      <td className="py-3.5 px-4 text-right text-amber-700 font-semibold">{formatWeightGrams(it.net_metal_weight_grams)}</td>
                      <td className="py-3.5 px-4 text-right text-slate-600 font-semibold">{formatCarat(it.total_stone_carats)}</td>
                      <td className="py-3.5 px-4 text-right font-mono text-slate-500">{formatCurrency(it.total_cost)}</td>
                      <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">{formatCurrency(it.selling_price)}</td>
                      <td className="py-3.5 px-4 text-center">
                        <Badge status={it.status} />
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <button
                          onClick={() => setSelectedItem(it)}
                          className="p-1 text-slate-500 hover:text-amber-600 rounded"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* View 2: Design Catalog Grid */}
      {activeSubTab === 'designs' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {designs.map((d) => (
            <div key={d.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
              <div className="h-44 bg-slate-100 relative overflow-hidden">
                {d.image_url ? (
                  <img src={d.image_url} alt={d.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-400">
                    <Sparkles className="w-10 h-10" />
                  </div>
                )}
                <span className="absolute top-3 right-3 px-2 py-0.5 bg-slate-900/80 text-white rounded text-[10px] font-mono">
                  {d.design_code}
                </span>
              </div>
              <div className="p-5">
                <div className="flex items-center justify-between text-xs text-amber-700 font-semibold mb-1">
                  <span>{d.category}</span>
                  <span>{d.purity} {d.metal_type}</span>
                </div>
                <h4 className="font-serif font-bold text-slate-800 text-base">{d.name}</h4>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">{d.description || 'No description'}</p>
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500">Active Stock:</span>
                  <span className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">{d.item_count || 0} pieces in vault</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Item Detail Modal */}
      {selectedItem && (
        <Modal
          isOpen={!!selectedItem}
          onClose={() => setSelectedItem(null)}
          title={`Jewellery Piece Details: ${selectedItem.sku}`}
        >
          <div className="space-y-6 text-xs">
            <div className="grid grid-cols-3 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-semibold">Gross Scale Weight</p>
                <p className="text-base font-bold text-slate-900 mt-0.5">{formatWeightGrams(selectedItem.gross_weight_grams)}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-semibold">Net Pure Metal Weight</p>
                <p className="text-base font-bold text-amber-700 mt-0.5">{formatWeightGrams(selectedItem.net_metal_weight_grams)}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-semibold">Total Studded Stones</p>
                <p className="text-base font-bold text-slate-900 mt-0.5">{formatCarat(selectedItem.total_stone_carats)}</p>
              </div>
            </div>

            <div className="border border-slate-200 rounded-xl overflow-hidden divide-y divide-slate-100">
              <div className="grid grid-cols-2 p-3 bg-slate-50/50">
                <span className="text-slate-500">Hallmarking Specification</span>
                <span className="font-semibold text-slate-800 text-right">{selectedItem.hallmark_details || '-'}</span>
              </div>
              <div className="grid grid-cols-2 p-3">
                <span className="text-slate-500">Metal Acquisition Cost</span>
                <span className="font-mono text-slate-700 text-right">{formatCurrency(selectedItem.metal_cost)}</span>
              </div>
              <div className="grid grid-cols-2 p-3 bg-slate-50/50">
                <span className="text-slate-500">Diamond & Gemstone Cost</span>
                <span className="font-mono text-slate-700 text-right">{formatCurrency(selectedItem.stone_cost)}</span>
              </div>
              <div className="grid grid-cols-2 p-3">
                <span className="text-slate-500">Making Charges</span>
                <span className="font-mono text-slate-700 text-right">{formatCurrency(selectedItem.making_charge)}</span>
              </div>
              <div className="grid grid-cols-2 p-3 bg-slate-50/50">
                <span className="text-slate-800 font-bold">Total Manufacturing / Acquisition Cost</span>
                <span className="font-mono font-bold text-slate-900 text-right">{formatCurrency(selectedItem.total_cost)}</span>
              </div>
              <div className="grid grid-cols-2 p-3 bg-amber-50/50">
                <span className="text-amber-900 font-bold">Current Selling Price</span>
                <span className="font-mono font-bold text-amber-800 text-right text-sm">{formatCurrency(selectedItem.selling_price)}</span>
              </div>
            </div>

            {selectedItem.stones && selectedItem.stones.length > 0 && (
              <div>
                <h4 className="font-serif font-bold text-slate-800 mb-2">Studded Stones Breakdown</h4>
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="p-2.5">Stone Type</th>
                        <th className="p-2.5">Count</th>
                        <th className="p-2.5">Carat Weight</th>
                        <th className="p-2.5">Setting</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {selectedItem.stones.map((st) => (
                        <tr key={st.id}>
                          <td className="p-2.5 font-medium">{st.stone_type} ({st.shape || 'Round'})</td>
                          <td className="p-2.5">{st.stone_count}</td>
                          <td className="p-2.5 font-semibold">{formatCarat(st.carat_weight)}</td>
                          <td className="p-2.5 text-slate-500">{st.setting_type || 'Prong'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Add Finished Piece Modal */}
      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Add Finished Jewellery Piece"
        maxWidth="2xl"
      >
        <form onSubmit={handleAddItem} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Item SKU *</label>
              <input
                type="text"
                required
                value={newItem.sku}
                onChange={(e) => setNewItem({ ...newItem, sku: e.target.value })}
                placeholder="JWL-2026-0043"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Master Design Template *</label>
              <select
                value={newItem.product_id}
                onChange={(e) => setNewItem({ ...newItem, product_id: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                {designs.map((d) => (
                  <option key={d.id} value={d.id}>{d.name} ({d.design_code})</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Gross Scale Weight (grams) *</label>
              <input
                type="number"
                step="0.001"
                required
                value={newItem.gross_weight_grams}
                onChange={(e) => setNewItem({ ...newItem, gross_weight_grams: e.target.value })}
                placeholder="4.850"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Net Metal Weight (grams) *</label>
              <input
                type="number"
                step="0.001"
                required
                value={newItem.net_metal_weight_grams}
                onChange={(e) => setNewItem({ ...newItem, net_metal_weight_grams: e.target.value })}
                placeholder="4.550"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Metal Cost (₹)</label>
              <input
                type="number"
                value={newItem.metal_cost}
                onChange={(e) => setNewItem({ ...newItem, metal_cost: e.target.value })}
                placeholder="32000"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Stone Cost (₹)</label>
              <input
                type="number"
                value={newItem.stone_cost}
                onChange={(e) => setNewItem({ ...newItem, stone_cost: e.target.value })}
                placeholder="450000"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Making Charges (₹)</label>
              <input
                type="number"
                value={newItem.making_charge}
                onChange={(e) => setNewItem({ ...newItem, making_charge: e.target.value })}
                placeholder="15000"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">Final Selling Price (INR) *</label>
            <input
              type="number"
              step="0.01"
              required
              value={newItem.selling_price}
              onChange={(e) => setNewItem({ ...newItem, selling_price: e.target.value })}
              placeholder="680000.00"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
            />
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-end gap-2">
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
              Save Piece to Vault
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Design Template Modal */}
      <Modal
        isOpen={isAddDesignOpen}
        onClose={() => setIsAddDesignOpen(false)}
        title="Create Master Design Template"
        maxWidth="md"
      >
        <form onSubmit={handleAddDesign} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-700 mb-1">Design Code *</label>
            <input
              type="text"
              required
              value={newDesign.design_code}
              onChange={(e) => setNewDesign({ ...newDesign, design_code: e.target.value })}
              placeholder="DES-RNG-04"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-mono"
            />
          </div>
          <div>
            <label className="block font-medium text-slate-700 mb-1">Design Title *</label>
            <input
              type="text"
              required
              value={newDesign.name}
              onChange={(e) => setNewDesign({ ...newDesign, name: e.target.value })}
              placeholder="Eternal Radiance Ring"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Category</label>
              <select
                value={newDesign.category}
                onChange={(e) => setNewDesign({ ...newDesign, category: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="Ring">Ring</option>
                <option value="Necklace">Necklace</option>
                <option value="Pendant">Pendant</option>
                <option value="Earrings">Earrings</option>
                <option value="Bracelet">Bracelet</option>
                <option value="Bangles">Bangles</option>
              </select>
            </div>
            <div>
              <label className="block font-medium text-slate-700 mb-1">Purity</label>
              <select
                value={newDesign.purity}
                onChange={(e) => setNewDesign({ ...newDesign, purity: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="18K">18K (750)</option>
                <option value="22K">22K (916)</option>
                <option value="14K">14K (585)</option>
                <option value="950 Pt">950 Platinum</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block font-medium text-slate-700 mb-1">Description</label>
            <textarea
              rows={2}
              value={newDesign.description}
              onChange={(e) => setNewDesign({ ...newDesign, description: e.target.value })}
              placeholder="Design motifs, setting styles..."
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="pt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAddDesignOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold"
            >
              Save Design
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
