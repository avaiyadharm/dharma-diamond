import React, { useState, useEffect } from 'react';
import { ShieldCheck, Search, User, Clock, AlertCircle } from 'lucide-react';
import api from '../api/client';
import { formatDate } from '../utils/formatters';

interface AuditLog {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  entity_type: string;
  entity_id: string;
  description: string;
  ip_address: string;
  created_at: string;
}

export const AuditView: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError('');
      const params: any = {};
      if (search) params.query = search;
      const res = await api.get('/audit/logs', { params });
      setLogs(res.data?.items || res.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [search]);

  const getActionColor = (action: string) => {
    if (!action) return 'bg-slate-100 text-slate-700';
    const a = action.toUpperCase();
    if (a.includes('CREATE') || a.includes('ADD')) return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
    if (a.includes('DELETE') || a.includes('REMOVE')) return 'bg-rose-50 text-rose-700 border border-rose-200';
    if (a.includes('UPDATE') || a.includes('EDIT') || a.includes('MODIFY')) return 'bg-blue-50 text-blue-700 border border-blue-200';
    if (a.includes('LOGIN') || a.includes('LOGOUT') || a.includes('AUTH')) return 'bg-amber-50 text-amber-700 border border-amber-200';
    return 'bg-slate-100 text-slate-700 border border-slate-200';
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto">
      {/* Search Bar */}
      <div className="flex items-center gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by user, action, entity..."
            className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500 text-slate-800"
          />
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <ShieldCheck className="w-4 h-4 text-amber-500" />
          <span>Full tamper-evident system audit trail</span>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="px-6 py-3 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
          <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
            System Audit Logs
          </p>
        </div>

        {error && (
          <div className="p-4 flex items-center gap-2 text-sm text-rose-600 bg-rose-50 border-b border-rose-100">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/80 uppercase tracking-wider font-semibold">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    Loading audit records...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    No audit log entries found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-500 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {formatDate(log.created_at)}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1.5">
                        <User className="w-3 h-3 text-slate-400" />
                        <span className="font-medium text-slate-800">{log.user_email || '-'}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold ${getActionColor(log.action)}`}>
                        {log.action || '-'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-slate-600">
                        {log.entity_type || '-'}
                        {log.entity_id && <span className="text-slate-400 ml-1">#{log.entity_id.slice(0, 8)}</span>}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600 max-w-xs truncate" title={log.description}>
                      {log.description || '-'}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-500">
                      {log.ip_address || '-'}
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
