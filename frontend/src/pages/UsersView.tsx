import React, { useState, useEffect } from 'react';
import { Users, Plus, Shield, CheckCircle, XCircle } from 'lucide-react';
import api from '../api/client';
import type { User } from '../types';
import { formatDate } from '../utils/formatters';
import { Modal } from '../components/common/Modal';

export const UsersView: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddOpen, setIsAddOpen] = useState(false);

  const [newUser, setNewUser] = useState({
    email: '',
    full_name: '',
    role: 'sales_staff',
    password: 'password123',
    is_active: true
  });

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.get('/auth/users');
      setUsers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/auth/users', newUser);
      setIsAddOpen(false);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create user account');
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h3 className="font-serif font-bold text-slate-800 text-base">User Management & Permissions (RBAC)</h3>
          <p className="text-xs text-slate-500">Configure role privileges for Vault Managers, Sales Staff, and Accountants</p>
        </div>

        <button
          onClick={() => setIsAddOpen(true)}
          className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Add Staff Account
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3.5 px-4">Full Name</th>
                <th className="py-3.5 px-4">Email</th>
                <th className="py-3.5 px-4">Role Privileges</th>
                <th className="py-3.5 px-4">Account Status</th>
                <th className="py-3.5 px-4">Last Login</th>
                <th className="py-3.5 px-4">Created Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-slate-900">{u.full_name}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-600">{u.email}</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200 uppercase tracking-wider">
                      {u.role.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    {u.is_active ? (
                      <span className="text-emerald-700 font-semibold flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" /> Active
                      </span>
                    ) : (
                      <span className="text-rose-600 font-semibold flex items-center gap-1">
                        <XCircle className="w-3.5 h-3.5" /> Disabled
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-slate-500">{formatDate(u.last_login_at)}</td>
                  <td className="py-3.5 px-4 text-slate-500">{formatDate(u.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Create Staff Account"
        maxWidth="md"
      >
        <form onSubmit={handleCreateUser} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-700 mb-1">Full Name *</label>
            <input
              type="text"
              required
              value={newUser.full_name}
              onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
              placeholder="Rajesh Kumar"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">Email Address *</label>
            <input
              type="email"
              required
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              placeholder="rajesh@dharmadiamond.com"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-mono"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">Assigned Role *</label>
            <select
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value as any })}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
            >
              <option value="sales_staff">Sales Staff (Checkout & Customer records)</option>
              <option value="inventory_manager">Inventory Manager (Inward Receipts & Stock)</option>
              <option value="accountant">Accountant (Invoices, Payments & Reports)</option>
              <option value="admin">Administrator (Full Access & User Control)</option>
              <option value="read_only">Read-Only User (Auditor / Viewer)</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-700 mb-1">Temporary Password *</label>
            <input
              type="text"
              required
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-mono"
            />
          </div>

          <div className="pt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAddOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold"
            >
              Create Account
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
