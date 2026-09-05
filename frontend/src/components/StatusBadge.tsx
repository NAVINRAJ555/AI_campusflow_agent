import React from 'react';
import { BookingStatus } from '../types';

interface StatusBadgeProps {
  status: BookingStatus | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const normalized = status.toUpperCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';

  switch (normalized) {
    case 'APPROVED':
      colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      break;
    case 'PENDING':
    case 'PROCESSING':
      colorClasses = 'bg-blue-50 text-blue-700 border-blue-200 animate-pulse';
      break;
    case 'CONFLICT':
      colorClasses = 'bg-rose-50 text-rose-700 border-rose-200 font-semibold';
      break;
    case 'NEGOTIATING':
      colorClasses = 'bg-amber-50 text-amber-700 border-amber-200';
      break;
    case 'RESCHEDULED':
      colorClasses = 'bg-indigo-50 text-indigo-700 border-indigo-200';
      break;
    case 'REJECTED':
      colorClasses = 'bg-red-50 text-red-700 border-red-200';
      break;
    case 'CANCELLED':
      colorClasses = 'bg-gray-100 text-gray-500 border-gray-200 line-through';
      break;
    case 'COMPLETED':
      colorClasses = 'bg-teal-50 text-teal-700 border-teal-200';
      break;
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center rounded-full border font-medium ${sizeClasses} ${colorClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-75"></span>
      {normalized}
    </span>
  );
};
