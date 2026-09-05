import React, { useEffect, useState } from 'react';
import { analyticsApi, bookingsApi, notificationsApi } from '../services/api';
import { AnalyticsOverview, Booking, NotificationItem } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { Link } from 'react-router-dom';
import {
  Building2,
  CalendarCheck,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Bell
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

export const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [recentBookings, setRecentBookings] = useState<Booking[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ovRes, bkRes, ntRes] = await Promise.all([
          analyticsApi.getOverview(),
          bookingsApi.getAll(),
          notificationsApi.getAll()
        ]);
        setOverview(ovRes.data);
        setRecentBookings(bkRes.data.slice(0, 6));
        setNotifications(ntRes.data.slice(0, 5));
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Loading CampusFlow Dashboard...</p>
        </div>
      </div>
    );
  }

  const metrics = overview?.performance_metrics;

  const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  const utilizationChartData = overview?.resource_utilization.map(r => ({
    name: r.resource_name.replace('Seminar Hall ', 'SH-').replace('Smart Classroom ', 'SC-').replace('Computer Lab ', 'Lab-').replace('Conference Room ', 'CR-'),
    utilization: r.utilization_percentage,
    hours: r.allocated_hours
  })) || [];

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-600 rounded-2xl p-6 text-white shadow-lg shadow-blue-600/15">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider bg-white/20 px-2.5 py-1 rounded-full text-white">
            Autonomous Multi-Agent Scheduler
          </span>
          <h1 className="text-2xl md:text-3xl font-bold mt-2">CampusFlow Intelligence Center</h1>
          <p className="text-sm text-blue-100 mt-1 max-w-2xl">
            Intelligent resource allocation, real-time policy evaluation, and automated multi-agent negotiation.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/create-booking"
            className="px-4 py-2.5 bg-white text-blue-700 font-semibold rounded-xl text-sm shadow-md hover:bg-blue-50 transition-all flex items-center space-x-2 shrink-0"
          >
            <Sparkles className="w-4 h-4 text-blue-600" />
            <span>AI Smart Booking</span>
          </Link>
        </div>
      </div>

      {/* Top Cards (Section 28) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Total Resources"
          value={overview?.total_resources || 0}
          subtitle="Auditoriums, Labs, Halls"
          icon={<Building2 className="w-5 h-5" />}
          highlightColor="blue"
        />
        <MetricCard
          title="Available Now"
          value={overview?.available_resources_now || 0}
          subtitle="Operational venues"
          icon={<CheckCircle2 className="w-5 h-5" />}
          highlightColor="green"
        />
        <MetricCard
          title="Total Bookings"
          value={overview?.total_bookings || 0}
          subtitle={`${overview?.approved_bookings || 0} confirmed`}
          icon={<CalendarCheck className="w-5 h-5" />}
          highlightColor="purple"
        />
        <MetricCard
          title="Active Conflicts"
          value={overview?.active_conflicts || 0}
          subtitle="Auto-negotiating"
          icon={<AlertTriangle className="w-5 h-5" />}
          highlightColor="rose"
        />
      </div>

      {/* University Performance Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Resource Utilization</span>
          <div className="text-xl font-bold text-slate-800 mt-1">{metrics?.resource_utilization_rate}%</div>
          <span className="text-[10px] text-slate-500">Target: &gt;65%</span>
        </div>
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Conflict Resolution Rate</span>
          <div className="text-xl font-bold text-emerald-600 mt-1">{metrics?.conflict_resolution_rate}%</div>
          <span className="text-[10px] text-slate-500">Autonomous resolution</span>
        </div>
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Fairness Index</span>
          <div className="text-xl font-bold text-blue-600 mt-1">{metrics?.fairness_index}%</div>
          <span className="text-[10px] text-slate-500">Multi-department balance</span>
        </div>
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Scheduling Accuracy</span>
          <div className="text-xl font-bold text-indigo-600 mt-1">{metrics?.scheduling_accuracy}%</div>
          <span className="text-[10px] text-slate-500">Zero constraint violations</span>
        </div>
      </div>

      {/* Visual Charts & Utilization (Section 28 Third Section) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-800 text-sm">Resource Utilization Breakdown</h3>
              <p className="text-xs text-slate-400">Allocated hours vs total available hours</p>
            </div>
            <Link to="/analytics" className="text-xs font-semibold text-blue-600 hover:underline flex items-center">
              <span>Detailed view</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={utilizationChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                <Tooltip
                  formatter={(val: any) => [`${val}%`, 'Utilization']}
                  contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="utilization" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Booking Status Distribution */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-slate-800 text-sm">Allocation Status Breakdown</h3>
            <p className="text-xs text-slate-400">Current status of all submitted requests</p>
          </div>

          <div className="h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={overview?.status_breakdown || []}
                  dataKey="count"
                  nameKey="status"
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={4}
                >
                  {(overview?.status_breakdown || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
            {(overview?.status_breakdown || []).slice(0, 4).map((s, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                <span className="text-slate-600 truncate">{s.status}:</span>
                <span className="font-bold text-slate-900">{s.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Second Section: Upcoming Bookings & Recent Notifications */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bookings Table */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-800 text-sm">Recent & Upcoming Bookings</h3>
              <p className="text-xs text-slate-400">Real-time schedule allocation records</p>
            </div>
            <Link to="/my-bookings" className="text-xs font-semibold text-blue-600 hover:underline flex items-center">
              <span>View all</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-400 uppercase font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-2.5 px-3">Event</th>
                  <th className="py-2.5 px-3">Venue</th>
                  <th className="py-2.5 px-3">Date & Time</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {recentBookings.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-slate-400">No bookings found</td>
                  </tr>
                ) : (
                  recentBookings.map(b => (
                    <tr key={b.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-semibold text-slate-900">{b.event_name}</div>
                        <div className="text-[10px] text-slate-400">{b.department_name || 'Academic Dept'}</div>
                      </td>
                      <td className="py-3 px-3 font-medium text-slate-800">
                        {b.resource_name || b.resource_type}
                      </td>
                      <td className="py-3 px-3">
                        <div>{b.date}</div>
                        <div className="text-[10px] text-slate-400">{b.start_time} - {b.end_time}</div>
                      </td>
                      <td className="py-3 px-3">
                        <PriorityBadge priority={b.priority} />
                      </td>
                      <td className="py-3 px-3">
                        <StatusBadge status={b.status} size="sm" />
                      </td>
                      <td className="py-3 px-3 text-right">
                        <Link
                          to={`/bookings/${b.id}`}
                          className="font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          Trace
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Notifications & Agent Feed */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Bell className="w-4 h-4 text-blue-600" />
                <h3 className="font-semibold text-slate-800 text-sm">Recent Alerts</h3>
              </div>
              <Link to="/notifications" className="text-xs text-blue-600 hover:underline">
                All
              </Link>
            </div>

            <div className="space-y-3">
              {notifications.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-4">No recent notifications</p>
              ) : (
                notifications.map(n => (
                  <div key={n.id} className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs">
                    <p className="text-slate-800 leading-snug">{n.message}</p>
                    <span className="text-[10px] text-slate-400 mt-1 block">
                      {new Date(n.created_at).toLocaleDateString()} at {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-gradient-to-br from-slate-900 to-blue-950 rounded-xl p-5 text-white shadow-sm">
            <div className="flex items-center space-x-2 mb-2">
              <BrainCircuit className="w-4 h-4 text-blue-400" />
              <h4 className="font-semibold text-sm text-blue-100">Deterministic Multi-Agent Engine</h4>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Every request executes through LangGraph stateful orchestration: Understand → Intelligence → Policy & Priority → Negotiation → OR-Tools Optimization → Explainable AI.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
