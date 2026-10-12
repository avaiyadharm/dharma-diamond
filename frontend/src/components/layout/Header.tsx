import React from 'react';
import { Search, Bell, Shield, Database } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface HeaderProps {
  title: string;
  subtitle?: string;
  searchTerm?: string;
  onSearchChange?: (val: string) => void;
  actionButton?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  searchTerm,
  onSearchChange,
  actionButton
}) => {
  const { user } = useAuth();

  return (
    <header className="h-16 px-8 border-b border-slate-200 bg-white flex items-center justify-between shrink-0 sticky top-0 z-20">
      <div>
        <h2 className="text-xl font-bold text-slate-800 font-serif leading-none">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {onSearchChange !== undefined && (
          <div className="relative w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm || ''}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Quick search SKU, Cert, Party..."
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition-all text-slate-800"
            />
          </div>
        )}

        {actionButton}

        <div className="h-6 w-px bg-slate-200" />

        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
            Vault Online (INR)
          </span>
        </div>
      </div>
    </header>
  );
};
