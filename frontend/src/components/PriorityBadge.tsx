import React from 'react';
import { PriorityLevel } from '../types';

interface PriorityBadgeProps {
  priority: PriorityLevel | string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority }) => {
  const normalized = priority.toUpperCase();

  let color = 'bg-slate-100 text-slate-700';

  if (normalized === 'VERY_HIGH') {
    color = 'bg-purple-100 text-purple-800 font-bold border border-purple-200';
  } else if (normalized === 'HIGH') {
    color = 'bg-amber-100 text-amber-800 font-medium border border-amber-200';
  } else if (normalized === 'MEDIUM') {
    color = 'bg-sky-100 text-sky-800 border border-sky-200';
  } else if (normalized === 'LOW') {
    color = 'bg-gray-100 text-gray-700 border border-gray-200';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs tracking-wide uppercase ${color}`}>
      {normalized.replace('_', ' ')}
    </span>
  );
};
