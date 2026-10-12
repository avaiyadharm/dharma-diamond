import React from 'react';
import {
  LayoutDashboard,
  Gem,
  Sparkles,
  ShoppingBag,
  ShoppingCart,
  FileText,
  CreditCard,
  ArrowLeftRight,
  Users,
  BarChart3,
  ShieldCheck,
  LogOut,
  Layers,
  CircleDot
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export type ActiveTab =
  | 'dashboard'
  | 'diamonds'
  | 'jewellery'
  | 'gemstones'
  | 'purchases'
  | 'sales'
  | 'invoices'
  | 'payments'
  | 'movements'
  | 'parties'
  | 'reports'
  | 'users'
  | 'audit';

interface SidebarProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const { user, logout, isAdmin } = useAuth();

  const navigation = [
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
    { id: 'diamonds', name: 'Diamond Inventory', icon: Gem },
    { id: 'jewellery', name: 'Jewellery Inventory', icon: Sparkles },
    { id: 'gemstones', name: 'Loose Gemstones', icon: CircleDot },
    { id: 'purchases', name: 'Purchases & Receipts', icon: ShoppingBag },
    { id: 'sales', name: 'Sales Orders', icon: ShoppingCart },
    { id: 'invoices', name: 'Invoices', icon: FileText },
    { id: 'payments', name: 'Payments', icon: CreditCard },
    { id: 'movements', name: 'Stock Movements', icon: ArrowLeftRight },
    { id: 'parties', name: 'Suppliers & Customers', icon: Users },
    { id: 'reports', name: 'Reports & Exports', icon: BarChart3 },
    ...(isAdmin
      ? [
          { id: 'users', name: 'User Management', icon: Users },
          { id: 'audit', name: 'Audit Logs', icon: ShieldCheck },
        ]
      : []),
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="h-18 px-6 flex items-center gap-3 border-b border-slate-800 bg-slate-950/50">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center text-slate-950 shadow-md">
          <Gem className="w-5 h-5 text-slate-950 stroke-[2.5]" />
        </div>
        <div>
          <h1 className="font-serif font-bold text-base tracking-wider text-white">DHARMA</h1>
          <p className="text-[10px] uppercase tracking-widest text-amber-400 font-semibold">Fine Diamond Vault</p>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          Core Operations
        </div>
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id as ActiveTab)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-amber-500/15 text-amber-300 border-l-2 border-amber-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
              <span className="truncate">{item.name}</span>
            </button>
          );
        })}
      </nav>

      {/* User Profile & Logout Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60">
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/80 border border-slate-800">
          <div className="min-w-0 pr-2">
            <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name}</p>
            <p className="text-[10px] text-amber-400 font-mono capitalize truncate">{user?.role?.replace('_', ' ')}</p>
          </div>
          <button
            onClick={logout}
            title="Sign Out"
            className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-md transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
