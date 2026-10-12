import React, { useState } from 'react';
import { Gem, Lock, Mail, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('admin@dharmadiamond.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Subtle Glows */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-amber-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 to-amber-700 items-center justify-center shadow-lg shadow-amber-500/20 mb-4">
            <Gem className="w-8 h-8 text-slate-950 stroke-[2.5]" />
          </div>
          <h1 className="font-serif text-2xl font-bold tracking-wider text-white">DHARMA DIAMOND</h1>
          <p className="text-xs uppercase tracking-widest text-amber-400/90 font-medium mt-1">
            Inventory & Record Management System
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl flex items-center gap-2.5 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@dharmadiamond.com"
                className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-semibold rounded-xl text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-amber-500/20 disabled:opacity-50"
          >
            {isLoading ? 'Authenticating...' : 'Sign In to Vault'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Demo Switcher */}
        <div className="mt-8 pt-6 border-t border-slate-800/80 text-center">
          <p className="text-[11px] text-slate-500 mb-3">Quick demo sign-in accounts:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            <button
              type="button"
              onClick={() => handleQuickLogin('admin@dharmadiamond.com', 'admin123')}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-[11px] text-amber-300 rounded-lg border border-slate-700 transition-colors"
            >
              SuperAdmin
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('manager@dharmadiamond.com', 'manager123')}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-300 rounded-lg border border-slate-700 transition-colors"
            >
              Vault Manager
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('sales@dharmadiamond.com', 'sales123')}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-300 rounded-lg border border-slate-700 transition-colors"
            >
              Senior Sales
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
