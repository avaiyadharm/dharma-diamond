import React from 'react';

interface BadgeProps {
  status: string;
  variant?: 'status' | 'cert' | 'metal' | 'role';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ status, variant = 'status', className = '' }) => {
  const getStyles = () => {
    switch (status.toUpperCase()) {
      case 'AVAILABLE':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'RESERVED':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'SOLD':
        return 'bg-slate-100 text-slate-700 border-slate-200';
      case 'MOUNTED':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      case 'DAMAGED':
      case 'CANCELLED':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'RECEIVED':
      case 'PAID':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'PARTIALLY_PAID':
      case 'PARTIALLY_RECEIVED':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'UNPAID':
      case 'ISSUED':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'CONFIRMED':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'GIA':
        return 'bg-blue-900 text-white border-blue-900 font-semibold';
      case 'IGI':
        return 'bg-amber-800 text-white border-amber-800 font-semibold';
      case 'HRD':
        return 'bg-teal-800 text-white border-teal-800 font-semibold';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStyles()} ${className}`}
    >
      {status}
    </span>
  );
};
