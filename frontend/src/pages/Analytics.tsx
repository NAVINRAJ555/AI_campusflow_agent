import React, { useEffect, useState } from 'react';
import { analyticsApi } from '../services/api';
import { AnalyticsOverview } from '../types';
import { MetricCard } from '../components/MetricCard';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  Legend
} from 'recharts';
import {
  Scale,
  Cpu,
  CheckCircle2,
  Clock,
  ShieldCheck,
  TrendingUp,
  Award,
  AlertTriangle
} from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.getOverview()
      .then(res => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const m = data.performance_metrics;

  const departmentChartData = data.department_fairness.map(d => ({
    name: d.department_name.split(' ')[0],
    Requests: d.total_requests,
    Approved: d.approved_requests,
    Satisfaction: d.satisfaction_rate
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">System Analytics & Performance Metrics</h1>
        <p className="text-xs text-slate-500 mt-1">
          Formal evaluation metrics based on institutional benchmarks and deterministic multi-agent telemetry.
        </p>
      </div>

      {/* 8 Mandated Performance Metrics (Section 18) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">1. Resource Utilization</span>
            <Cpu className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{m.resource_utilization_rate}%</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Allocated / Total Hours × 100
          </div>
        </div>

        {/* Metric 2 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">2. Conflict Resolution Rate</span>
            <Award className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-600">{m.conflict_resolution_rate}%</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Resolved / Total Conflicts × 100
          </div>
        </div>

        {/* Metric 3 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">3. Average Allocation Time</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{m.average_allocation_time_seconds}s</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Total Proc Time / Requests
          </div>
        </div>

        {/* Metric 4 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">4. Policy Compliance Rate</span>
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-indigo-600">{m.policy_compliance_rate}%</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Compliant Allocations / Total × 100
          </div>
        </div>

        {/* Metric 5 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">5. Fairness Index</span>
            <Scale className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-blue-600">{m.fairness_index}%</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Satisfied / Total Requests × 100
          </div>
        </div>

        {/* Metric 6 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">6. User Satisfaction Score</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{m.user_satisfaction_score} / 5.0</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Sum Ratings / Number of Users
          </div>
        </div>

        {/* Metric 7 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">7. Manual Intervention Rate</span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{m.manual_intervention_rate}%</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Manual Requests / Total × 100
          </div>
        </div>

        {/* Metric 8 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[10px] font-bold uppercase tracking-wider">8. Scheduling Accuracy</span>
            <CheckCircle2 className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-purple-600">{m.scheduling_accuracy}%</div>
          <div className="text-[10px] text-slate-400 font-mono bg-slate-50 p-1.5 rounded">
            Successful / Total Requests × 100
          </div>
        </div>
      </div>

      {/* Department Fairness Comparison Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
        <div>
          <h3 className="font-bold text-slate-900 text-base">Department Fairness & Request Satisfaction</h3>
          <p className="text-xs text-slate-500">
            Guarantees balanced institutional resource access; prevents single-department scheduling dominance.
          </p>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={departmentChartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="Requests" fill="#94a3b8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Approved" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b">
              <tr>
                <th className="py-2.5 px-3">Department</th>
                <th className="py-2.5 px-3">Total Requests</th>
                <th className="py-2.5 px-3">Approved</th>
                <th className="py-2.5 px-3">Allocated Hours</th>
                <th className="py-2.5 px-3 text-right">Satisfaction Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y text-slate-700">
              {data.department_fairness.map(d => (
                <tr key={d.department_id}>
                  <td className="py-2.5 px-3 font-semibold text-slate-800">{d.department_name}</td>
                  <td className="py-2.5 px-3">{d.total_requests}</td>
                  <td className="py-2.5 px-3">{d.approved_requests}</td>
                  <td className="py-2.5 px-3">{d.allocated_hours} hrs</td>
                  <td className="py-2.5 px-3 text-right font-bold text-emerald-600">{d.satisfaction_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
