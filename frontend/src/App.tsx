import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { Sidebar, type ActiveTab } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { DashboardView } from './pages/DashboardView';
import { DiamondsView } from './pages/DiamondsView';
import { JewelleryView } from './pages/JewelleryView';
import { GemstonesView } from './pages/GemstonesView';
import { PurchasesView } from './pages/PurchasesView';
import { SalesView } from './pages/SalesView';
import { InvoicesView } from './pages/InvoicesView';
import { PaymentsView } from './pages/PaymentsView';
import { StockMovementsView } from './pages/StockMovementsView';
import { PartiesView } from './pages/PartiesView';
import { ReportsView } from './pages/ReportsView';
import { UsersView } from './pages/UsersView';
import { AuditView } from './pages/AuditView';

const PAGE_TITLES: Record<ActiveTab, { title: string; subtitle: string }> = {
  dashboard: { title: 'Dashboard', subtitle: 'Live business overview and key performance indicators' },
  diamonds: { title: 'Diamond Inventory', subtitle: 'Manage certified and non-certified loose diamonds' },
  jewellery: { title: 'Jewellery Inventory', subtitle: 'Track finished jewellery pieces and sets' },
  gemstones: { title: 'Loose Gemstones', subtitle: 'Manage coloured gemstone parcels and stones' },
  purchases: { title: 'Purchases & Receipts', subtitle: 'Record supplier purchases and goods received' },
  sales: { title: 'Sales Orders', subtitle: 'Create and manage customer sales orders' },
  invoices: { title: 'Invoices', subtitle: 'Generate and track customer invoices' },
  payments: { title: 'Payments', subtitle: 'Record and track payment transactions' },
  movements: { title: 'Stock Movements', subtitle: 'Audit trail of all inventory transfers and adjustments' },
  parties: { title: 'Suppliers & Customers', subtitle: 'Manage supplier and customer master records' },
  reports: { title: 'Reports & Exports', subtitle: 'Generate business reports and export data' },
  users: { title: 'User Management', subtitle: 'Manage staff accounts and role permissions' },
  audit: { title: 'Audit Logs', subtitle: 'Full system audit trail for compliance and security' },
};

const AppShell: React.FC = () => {
  const { user, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full border-4 border-amber-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 text-sm">Initialising Dharma Diamond Vault...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':    return <DashboardView />;
      case 'diamonds':     return <DiamondsView />;
      case 'jewellery':    return <JewelleryView />;
      case 'gemstones':    return <GemstonesView />;
      case 'purchases':    return <PurchasesView />;
      case 'sales':        return <SalesView />;
      case 'invoices':     return <InvoicesView />;
      case 'payments':     return <PaymentsView />;
      case 'movements':    return <StockMovementsView />;
      case 'parties':      return <PartiesView />;
      case 'reports':      return <ReportsView />;
      case 'users':        return <UsersView />;
      case 'audit':        return <AuditView />;
      default:             return <DashboardView />;
    }
  };

  const { title, subtitle } = PAGE_TITLES[activeTab];

  return (
    <div className="flex h-screen bg-slate-100 overflow-hidden">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-y-auto bg-slate-50">
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;
