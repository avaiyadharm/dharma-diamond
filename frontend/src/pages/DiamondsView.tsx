import React, { useState, useEffect } from 'react';
import {
  Gem,
  Plus,
  Filter,
  Search,
  ExternalLink,
  Shield,
  Clock,
  Eye,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import api from '../api/client';
import type { Diamond, Customer, Location, Supplier } from '../types';
import { formatCurrency, formatCarat, formatDate } from '../utils/formatters';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';

export const DiamondsView: React.FC = () => {
  const { isInventoryManager, isSalesStaff } = useAuth();
  const [diamonds, setDiamonds] = useState<Diamond[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [total, setTotal] = useState<number>(0);

  // Filters
  const [search, setSearch] = useState<string>('');
  const [selectedShape, setSelectedShape] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [minCarat, setMinCarat] = useState<string>('');
  const [maxCarat, setMaxCarat] = useState<string>('');

  // Modals
  const [isAddOpen, setIsAddOpen] = useState<boolean>(false);
  const [selectedDiamond, setSelectedDiamond] = useState<Diamond | null>(null);
  const [isReserveOpen, setIsReserveOpen] = useState<boolean>(false);

  // Dropdown master records
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);

  // Reservation Form State
  const [reserveCustomerId, setReserveCustomerId] = useState<string>('');
  const [reserveHours, setReserveHours] = useState<number>(48);

  // New Diamond Form State
  const [newDiamond, setNewDiamond] = useState({
    sku: '',
    shape: 'Round',
    carat_weight: '',
    color_grade: 'D',
    clarity_grade: 'VVS1',
    cut_grade: 'Excellent',
    polish: 'Excellent',
    symmetry: 'Excellent',
    fluorescence: 'None',
    measurements_mm: '',
    table_pct: '',
    depth_pct: '',
    diamond_type: 'Natural',
    certificate_lab: 'GIA',
    certificate_number: '',
    purchase_cost: '',
    asking_price: '',
    location_id: '',
    supplier_id: '',
    notes: ''
  });

  const [formError, setFormError] = useState<string>('');

  const fetchDiamonds = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (search) params.query = search;
      if (selectedShape) params.shape = selectedShape;
      if (selectedStatus) params.status = selectedStatus;
      if (minCarat) params.min_carat = minCarat;
      if (maxCarat) params.max_carat = maxCarat;

      const res = await api.get('/diamonds', { params });
      setDiamonds(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMasterData = async () => {
    try {
      const [cRes, lRes, sRes] = await Promise.all([
        api.get('/parties/customers'),
        api.get('/inventory/locations'),
        api.get('/parties/suppliers')
      ]);
      setCustomers(cRes.data);
      setLocations(lRes.data);
      setSuppliers(sRes.data);
      if (lRes.data.length > 0) {
        setNewDiamond(prev => ({ ...prev, location_id: lRes.data[0].id }));
      }
      if (sRes.data.length > 0) {
        setNewDiamond(prev => ({ ...prev, supplier_id: sRes.data[0].id }));
      }
    } catch (err) {
      console.error('Failed to load locations/parties', err);
    }
  };

  useEffect(() => {
    fetchDiamonds();
  }, [search, selectedShape, selectedStatus, minCarat, maxCarat]);

  useEffect(() => {
    fetchMasterData();
  }, []);

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      await api.post('/diamonds', {
        ...newDiamond,
        carat_weight: parseFloat(newDiamond.carat_weight),
        purchase_cost: parseFloat(newDiamond.purchase_cost),
        asking_price: parseFloat(newDiamond.asking_price),
        table_pct: newDiamond.table_pct ? parseFloat(newDiamond.table_pct) : undefined,
        depth_pct: newDiamond.depth_pct ? parseFloat(newDiamond.depth_pct) : undefined,
      });
      setIsAddOpen(false);
      fetchDiamonds();
      setNewDiamond({
        sku: '',
        shape: 'Round',
        carat_weight: '',
        color_grade: 'D',
        clarity_grade: 'VVS1',
        cut_grade: 'Excellent',
        polish: 'Excellent',
        symmetry: 'Excellent',
        fluorescence: 'None',
        measurements_mm: '',
        table_pct: '',
        depth_pct: '',
        diamond_type: 'Natural',
        certificate_lab: 'GIA',
        certificate_number: '',
        purchase_cost: '',
        asking_price: '',
        location_id: locations[0]?.id || '',
        supplier_id: suppliers[0]?.id || '',
        notes: ''
      });
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to add diamond');
    }
  };

  const handleReserve = async () => {
    if (!selectedDiamond || !reserveCustomerId) return;
    try {
      await api.post(`/diamonds/${selectedDiamond.id}/reserve`, {
        customer_id: reserveCustomerId,
        expires_in_hours: reserveHours
      });
      setIsReserveOpen(false);
      fetchDiamonds();
      if (selectedDiamond) {
        setSelectedDiamond({ ...selectedDiamond, status: 'RESERVED' });
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Reservation failed');
    }
  };

  const handleRelease = async (diamondId: string) => {
    try {
      await api.post(`/diamonds/${diamondId}/release`);
      fetchDiamonds();
      if (selectedDiamond) {
        setSelectedDiamond({ ...selectedDiamond, status: 'AVAILABLE' });
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Release failed');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      {/* Top Controls Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          <div className="relative min-w-[200px] flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter by SKU or GIA Cert #..."
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500 text-slate-800"
            />
          </div>

          <select
            value={selectedShape}
            onChange={(e) => setSelectedShape(e.target.value)}
            className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none"
          >
            <option value="">All Shapes</option>
            <option value="Round">Round</option>
            <option value="Oval">Oval</option>
            <option value="Emerald">Emerald</option>
            <option value="Princess">Princess</option>
            <option value="Cushion">Cushion</option>
            <option value="Pear">Pear</option>
            <option value="Radiant">Radiant</option>
            <option value="Heart">Heart</option>
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="AVAILABLE">Available</option>
            <option value="RESERVED">Reserved</option>
            <option value="SOLD">Sold</option>
            <option value="MOUNTED">Mounted</option>
          </select>

          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <input
              type="number"
              step="0.1"
              value={minCarat}
              onChange={(e) => setMinCarat(e.target.value)}
              placeholder="Min ct"
              className="w-18 px-2 py-2 bg-slate-50 border border-slate-200 rounded-lg text-center"
            />
            <span>-</span>
            <input
              type="number"
              step="0.1"
              value={maxCarat}
              onChange={(e) => setMaxCarat(e.target.value)}
              placeholder="Max ct"
              className="w-18 px-2 py-2 bg-slate-50 border border-slate-200 rounded-lg text-center"
            />
          </div>
        </div>

        {isInventoryManager && (
          <button
            onClick={() => setIsAddOpen(true)}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 shadow-sm transition-colors shrink-0"
          >
            <Plus className="w-4 h-4" />
            Add New Diamond
          </button>
        )}
      </div>

      {/* Diamonds Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="px-6 py-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Total Diamonds Found: <span className="text-slate-900">{total}</span>
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3 px-4">SKU / ID</th>
                <th className="py-3 px-4">Shape</th>
                <th className="py-3 px-4">Carat</th>
                <th className="py-3 px-4">Color</th>
                <th className="py-3 px-4">Clarity</th>
                <th className="py-3 px-4">Cut / Polish</th>
                <th className="py-3 px-4">Lab & Cert #</th>
                <th className="py-3 px-4 text-right">Cost Price</th>
                <th className="py-3 px-4 text-right">Asking Price</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-slate-400">
                    Loading inventory records...
                  </td>
                </tr>
              ) : diamonds.length === 0 ? (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-slate-400">
                    No diamond records match the selected criteria.
                  </td>
                </tr>
              ) : (
                diamonds.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-900">{d.sku}</td>
                    <td className="py-3.5 px-4 font-medium">{d.shape}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">{formatCarat(d.carat_weight)}</td>
                    <td className="py-3.5 px-4 font-medium">{d.color_grade}</td>
                    <td className="py-3.5 px-4 font-medium">{d.clarity_grade}</td>
                    <td className="py-3.5 px-4 text-slate-500">{d.cut_grade || '-'} / {d.polish || '-'}</td>
                    <td className="py-3.5 px-4">
                      {d.certificate_lab !== 'None' ? (
                        <div className="flex items-center gap-1.5">
                          <Badge status={d.certificate_lab} variant="cert" />
                          <span className="font-mono text-slate-600 text-[11px]">{d.certificate_number || '-'}</span>
                        </div>
                      ) : (
                        <span className="text-slate-400">Non-certified</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right text-slate-500 font-mono">{formatCurrency(d.purchase_cost)}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-slate-900 font-mono">{formatCurrency(d.asking_price)}</td>
                    <td className="py-3.5 px-4 text-center">
                      <Badge status={d.status} />
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => setSelectedDiamond(d)}
                          title="View Specifications"
                          className="p-1 text-slate-500 hover:text-amber-600 hover:bg-slate-100 rounded transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {d.status === 'AVAILABLE' && isSalesStaff && (
                          <button
                            onClick={() => {
                              setSelectedDiamond(d);
                              setIsReserveOpen(true);
                            }}
                            title="Reserve for Customer"
                            className="p-1 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded transition-colors"
                          >
                            <Clock className="w-4 h-4" />
                          </button>
                        )}
                        {d.status === 'RESERVED' && isSalesStaff && (
                          <button
                            onClick={() => handleRelease(d.id)}
                            title="Release Reservation"
                            className="p-1 text-amber-600 hover:text-emerald-600 hover:bg-slate-100 rounded transition-colors"
                          >
                            <CheckCircle className="w-4 h-4" />
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

      {/* View Diamond Details Modal */}
      {selectedDiamond && (
        <Modal
          isOpen={!!selectedDiamond && !isReserveOpen}
          onClose={() => setSelectedDiamond(null)}
          title={`Diamond Specifications: ${selectedDiamond.sku}`}
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Shape</p>
                <p className="text-sm font-bold text-slate-800 mt-0.5">{selectedDiamond.shape}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Carat Weight</p>
                <p className="text-sm font-bold text-slate-800 mt-0.5">{formatCarat(selectedDiamond.carat_weight)}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Color / Clarity</p>
                <p className="text-sm font-bold text-slate-800 mt-0.5">{selectedDiamond.color_grade} / {selectedDiamond.clarity_grade}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Status</p>
                <div className="mt-1">
                  <Badge status={selectedDiamond.status} />
                </div>
              </div>
            </div>

            <div className="border border-slate-200 rounded-xl overflow-hidden divide-y divide-slate-100 text-xs">
              <div className="grid grid-cols-2 p-3 bg-slate-50/50">
                <span className="text-slate-500">Cut / Polish / Symmetry</span>
                <span className="font-semibold text-slate-800 text-right">
                  {selectedDiamond.cut_grade || '-'} / {selectedDiamond.polish || '-'} / {selectedDiamond.symmetry || '-'}
                </span>
              </div>
              <div className="grid grid-cols-2 p-3">
                <span className="text-slate-500">Fluorescence</span>
                <span className="font-semibold text-slate-800 text-right">{selectedDiamond.fluorescence || 'None'}</span>
              </div>
              <div className="grid grid-cols-2 p-3 bg-slate-50/50">
                <span className="text-slate-500">Measurements (L x W x D)</span>
                <span className="font-semibold text-slate-800 text-right">{selectedDiamond.measurements_mm || '-'}</span>
              </div>
              <div className="grid grid-cols-2 p-3">
                <span className="text-slate-500">Table % / Depth %</span>
                <span className="font-semibold text-slate-800 text-right">
                  {selectedDiamond.table_pct ? `${selectedDiamond.table_pct}%` : '-'} / {selectedDiamond.depth_pct ? `${selectedDiamond.depth_pct}%` : '-'}
                </span>
              </div>
              <div className="grid grid-cols-2 p-3 bg-slate-50/50">
                <span className="text-slate-500">Certificate Lab & Number</span>
                <span className="font-semibold text-slate-800 text-right">
                  {selectedDiamond.certificate_lab} • {selectedDiamond.certificate_number || 'None'}
                </span>
              </div>
              <div className="grid grid-cols-2 p-3">
                <span className="text-slate-500">Inventory Vault Location</span>
                <span className="font-semibold text-slate-800 text-right">{selectedDiamond.location_name || 'Main Vault'}</span>
              </div>
              <div className="grid grid-cols-2 p-3 bg-slate-50/50">
                <span className="text-slate-500">Purchase Acquisition Cost</span>
                <span className="font-mono text-slate-700 text-right">{formatCurrency(selectedDiamond.purchase_cost)}</span>
              </div>
              <div className="grid grid-cols-2 p-3">
                <span className="text-slate-800 font-bold">Asking Retail Price</span>
                <span className="font-mono font-bold text-amber-700 text-right text-sm">{formatCurrency(selectedDiamond.asking_price)}</span>
              </div>
            </div>

            {selectedDiamond.notes && (
              <div className="p-3 bg-amber-50/50 border border-amber-200/80 rounded-xl text-xs text-amber-900">
                <p className="font-semibold mb-1">Gemologist Notes:</p>
                <p>{selectedDiamond.notes}</p>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Reserve Diamond Modal */}
      {selectedDiamond && isReserveOpen && (
        <Modal
          isOpen={isReserveOpen}
          onClose={() => setIsReserveOpen(false)}
          title={`Hold / Reserve: ${selectedDiamond.sku}`}
          maxWidth="md"
        >
          <div className="space-y-4 text-xs">
            <p className="text-slate-600">
              Holding a diamond blocks it from other sales orders and guarantees atomic reservation in the vault.
            </p>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Select Customer</label>
              <select
                value={reserveCustomerId}
                onChange={(e) => setReserveCustomerId(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                <option value="">-- Choose Customer --</option>
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} {c.company_name ? `(${c.company_name})` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Hold Duration (Hours)</label>
              <input
                type="number"
                value={reserveHours}
                onChange={(e) => setReserveHours(parseInt(e.target.value) || 24)}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              />
            </div>

            <div className="pt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsReserveOpen(false)}
                className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={!reserveCustomerId}
                onClick={handleReserve}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold disabled:opacity-50"
              >
                Confirm Hold
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Add New Diamond Modal */}
      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Register New Certified Diamond"
        maxWidth="3xl"
      >
        <form onSubmit={handleAddSubmit} className="space-y-5 text-xs">
          {formError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Stock SKU *</label>
              <input
                type="text"
                required
                value={newDiamond.sku}
                onChange={(e) => setNewDiamond({ ...newDiamond, sku: e.target.value })}
                placeholder="DIA-2026-0042"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-mono"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Shape *</label>
              <select
                value={newDiamond.shape}
                onChange={(e) => setNewDiamond({ ...newDiamond, shape: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                <option value="Round">Round</option>
                <option value="Oval">Oval</option>
                <option value="Emerald">Emerald</option>
                <option value="Princess">Princess</option>
                <option value="Cushion">Cushion</option>
                <option value="Pear">Pear</option>
                <option value="Radiant">Radiant</option>
                <option value="Heart">Heart</option>
                <option value="Asscher">Asscher</option>
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Carat Weight *</label>
              <input
                type="number"
                step="0.001"
                required
                value={newDiamond.carat_weight}
                onChange={(e) => setNewDiamond({ ...newDiamond, carat_weight: e.target.value })}
                placeholder="1.500"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Color Grade *</label>
              <select
                value={newDiamond.color_grade}
                onChange={(e) => setNewDiamond({ ...newDiamond, color_grade: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                {['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Fancy'].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Clarity Grade *</label>
              <select
                value={newDiamond.clarity_grade}
                onChange={(e) => setNewDiamond({ ...newDiamond, clarity_grade: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                {['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1'].map((cl) => (
                  <option key={cl} value={cl}>{cl}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Cut Grade</label>
              <select
                value={newDiamond.cut_grade}
                onChange={(e) => setNewDiamond({ ...newDiamond, cut_grade: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                {['Ideal', 'Excellent', 'Very Good', 'Good', 'Fair'].map((cg) => (
                  <option key={cg} value={cg}>{cg}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Diamond Type</label>
              <select
                value={newDiamond.diamond_type}
                onChange={(e) => setNewDiamond({ ...newDiamond, diamond_type: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                <option value="Natural">Natural Earth-Mined</option>
                <option value="Lab_Grown">Lab Grown (CVD/HPHT)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Certificate Lab</label>
              <select
                value={newDiamond.certificate_lab}
                onChange={(e) => setNewDiamond({ ...newDiamond, certificate_lab: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                <option value="GIA">GIA (Gemological Institute of America)</option>
                <option value="IGI">IGI (International Gemological Institute)</option>
                <option value="HRD">HRD Antwerp</option>
                <option value="SGL">SGL</option>
                <option value="None">In-House / Non-certified</option>
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Certificate #</label>
              <input
                type="text"
                value={newDiamond.certificate_number}
                onChange={(e) => setNewDiamond({ ...newDiamond, certificate_number: e.target.value })}
                placeholder="2195048123"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-mono"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Measurements (mm)</label>
              <input
                type="text"
                value={newDiamond.measurements_mm}
                onChange={(e) => setNewDiamond({ ...newDiamond, measurements_mm: e.target.value })}
                placeholder="7.32 x 7.36 x 4.54 mm"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Purchase Acquisition Cost (INR) *</label>
              <input
                type="number"
                step="0.01"
                required
                value={newDiamond.purchase_cost}
                onChange={(e) => setNewDiamond({ ...newDiamond, purchase_cost: e.target.value })}
                placeholder="450000.00"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-mono"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Asking Retail Price (INR) *</label>
              <input
                type="number"
                step="0.01"
                required
                value={newDiamond.asking_price}
                onChange={(e) => setNewDiamond({ ...newDiamond, asking_price: e.target.value })}
                placeholder="620000.00"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Vault Storage Location</label>
              <select
                value={newDiamond.location_id}
                onChange={(e) => setNewDiamond({ ...newDiamond, location_id: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>{loc.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Supplier</label>
              <select
                value={newDiamond.supplier_id}
                onChange={(e) => setNewDiamond({ ...newDiamond, supplier_id: e.target.value })}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              >
                {suppliers.map((s) => (
                  <option key={s.id} value={s.id}>{s.business_name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">Gemologist Notes</label>
            <textarea
              rows={2}
              value={newDiamond.notes}
              onChange={(e) => setNewDiamond({ ...newDiamond, notes: e.target.value })}
              placeholder="Inclusions, facet characteristics, fluorescence notes..."
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
            />
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAddOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold shadow-sm"
            >
              Register Diamond
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
