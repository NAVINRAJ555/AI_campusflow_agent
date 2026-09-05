import React, { useEffect, useState } from 'react';
import { auditLogsApi } from '../services/api';
import { AuditLogItem } from '../types';
import { ClipboardList, ShieldAlert, Clock, User, ArrowRight } from 'lucide-react';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    auditLogsApi.getAll()
      .then(res => setLogs(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center space-x-2">
          <ClipboardList className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-slate-900">System Audit Trail</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Immutable institutional audit trail of all booking creations, autonomous allocations, and administrative manual overrides.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Triggered By</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Audit Metadata</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-400">Loading audit trail...</td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-400">No audit logs recorded yet.</td>
                </tr>
              ) : logs.map(l => (
                <tr key={l.id} className="hover:bg-slate-50/60">
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500">
                    {new Date(l.created_at).toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      l.action.includes('OVERRIDE')
                        ? 'bg-purple-100 text-purple-800 border border-purple-200'
                        : l.action.includes('AGENT')
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-blue-50 text-blue-700 border border-blue-200'
                    }`}>
                      {l.action}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-semibold text-slate-800">{l.user_name}</td>
                  <td className="py-3.5 px-4 font-medium text-slate-600">
                    {l.entity_type} #{l.entity_id}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-600 max-w-md truncate">
                    {JSON.stringify(l.metadata)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
