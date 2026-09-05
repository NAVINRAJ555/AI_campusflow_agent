import React, { useState } from 'react';
import { AgentTraceStep } from '../types';
import {
  Brain,
  Search,
  Scale,
  GitPullRequest,
  Cpu,
  MessageSquare,
  ChevronDown,
  ChevronRight,
  Clock,
  CheckCircle2
} from 'lucide-react';

interface AgentTraceViewerProps {
  steps: AgentTraceStep[];
  totalTimeMs?: number;
}

export const AgentTraceViewer: React.FC<AgentTraceViewerProps> = ({ steps, totalTimeMs }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  const getAgentIcon = (name: string) => {
    if (name.includes('Understanding')) return <Brain className="w-5 h-5 text-blue-600" />;
    if (name.includes('Resource')) return <Search className="w-5 h-5 text-emerald-600" />;
    if (name.includes('Policy')) return <Scale className="w-5 h-5 text-indigo-600" />;
    if (name.includes('Negotiation')) return <GitPullRequest className="w-5 h-5 text-amber-600" />;
    if (name.includes('Optimization')) return <Cpu className="w-5 h-5 text-purple-600" />;
    return <MessageSquare className="w-5 h-5 text-teal-600" />;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Brain className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-slate-800">Multi-Agent Execution Pipeline</h3>
        </div>
        {totalTimeMs !== undefined && (
          <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-medium bg-white px-2.5 py-1 rounded-md border border-slate-200">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Total execution: {Math.round(totalTimeMs)} ms</span>
          </div>
        )}
      </div>

      <div className="divide-y divide-slate-100">
        {steps.map((step, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div key={idx} className="transition-colors hover:bg-slate-50/50">
              <div
                onClick={() => toggleExpand(idx)}
                className="p-4 flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center space-x-3.5">
                  <div className="p-2 rounded-lg bg-slate-100 border border-slate-200/60">
                    {getAgentIcon(step.agent_name)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        Step {idx + 1}
                      </span>
                      <h4 className="text-sm font-semibold text-slate-800">{step.agent_name}</h4>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">{step.summary}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="inline-flex items-center text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Success
                  </span>
                  <span className="text-xs text-slate-400">{Math.round(step.execution_time_ms)}ms</span>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="px-4 pb-4 pt-1 bg-slate-50/80 border-t border-slate-100 text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                    <div>
                      <p className="font-semibold text-slate-600 mb-1">Agent Input Snapshot:</p>
                      <pre className="p-3 bg-slate-900 text-slate-100 rounded-lg font-mono text-[11px] overflow-x-auto max-h-48">
                        {JSON.stringify(step.input_snapshot, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <p className="font-semibold text-slate-600 mb-1">Agent Output Snapshot:</p>
                      <pre className="p-3 bg-slate-900 text-emerald-400 rounded-lg font-mono text-[11px] overflow-x-auto max-h-48">
                        {JSON.stringify(step.output_snapshot, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
