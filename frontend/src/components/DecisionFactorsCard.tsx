import React from 'react';
import { StructuredDecisionFactors } from '../types';
import { ShieldCheck, Users, Clock, Cpu, GitCommit, Scale, Info } from 'lucide-react';

interface DecisionFactorsCardProps {
  factors: StructuredDecisionFactors;
}

export const DecisionFactorsCard: React.FC<DecisionFactorsCardProps> = ({ factors }) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <div className="flex items-center space-x-2 pb-4 border-b border-slate-100">
        <ShieldCheck className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-slate-800 text-lg">AI Transparent Decision Factors</h3>
      </div>

      <p className="mt-3 text-sm text-slate-600 italic bg-blue-50/50 p-3 rounded-lg border border-blue-100">
        "{factors.final_reason}"
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
        <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <ShieldCheck className="w-5 h-5 text-indigo-600 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-bold uppercase text-slate-500">Priority Consideration</span>
            <p className="text-sm text-slate-700 mt-0.5">{factors.priority_factor}</p>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <Users className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-bold uppercase text-slate-500">Capacity Satisfaction</span>
            <p className="text-sm text-slate-700 mt-0.5">{factors.capacity_factor}</p>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <Clock className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-bold uppercase text-slate-500">Time Alignment</span>
            <p className="text-sm text-slate-700 mt-0.5">{factors.time_factor}</p>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <Cpu className="w-5 h-5 text-purple-600 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-bold uppercase text-slate-500">Equipment Match</span>
            <p className="text-sm text-slate-700 mt-0.5">{factors.equipment_factor}</p>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <GitCommit className="w-5 h-5 text-rose-600 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-bold uppercase text-slate-500">Conflict Resolution</span>
            <p className="text-sm text-slate-700 mt-0.5">{factors.conflict_factor}</p>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <Scale className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-bold uppercase text-slate-500">Department Fairness</span>
            <p className="text-sm text-slate-700 mt-0.5">{factors.fairness_factor}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
