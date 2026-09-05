import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { bookingsApi, schedulingApi, resourcesApi } from '../services/api';
import { Booking, AgentTraceResponse, Resource, StructuredDecisionFactors } from '../types';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { AgentTraceViewer } from '../components/AgentTraceViewer';
import { DecisionFactorsCard } from '../components/DecisionFactorsCard';
import {
  Calendar,
  Clock,
  Building2,
  Users,
  ShieldCheck,
  Cpu,
  ArrowLeft,
  Settings2,
  AlertTriangle,
  Sparkles
} from 'lucide-react';

export const BookingDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const bookingId = Number(id);

  const [booking, setBooking] = useState<Booking | null>(null);
  const [trace, setTrace] = useState<AgentTraceResponse | null>(null);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);

  // Admin Override Form State
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideResourceId, setOverrideResourceId] = useState<number>(1);
  const [overrideDate, setOverrideDate] = useState('');
  const [overrideStartTime, setOverrideStartTime] = useState('10:00');
  const [overrideEndTime, setOverrideEndTime] = useState('13:00');
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideSubmitting, setOverrideSubmitting] = useState(false);

  const isAdminOrManager = user?.role === 'SYSTEM_ADMIN' || user?.role === 'RESOURCE_MANAGER';

  const fetchData = async () => {
    setLoading(true);
    try {
      const [bkRes, trRes, resList] = await Promise.all([
        bookingsApi.getById(bookingId),
        schedulingApi.getAgentTrace(bookingId),
        resourcesApi.getAll()
      ]);
      setBooking(bkRes.data);
      setTrace(trRes.data);
      setResources(resList.data);

      setOverrideResourceId(bkRes.data.resource_id || resList.data[0]?.id || 1);
      setOverrideDate(bkRes.data.date);
      setOverrideStartTime(bkRes.data.start_time);
      setOverrideEndTime(bkRes.data.end_time);
    } catch (err) {
      console.error('Failed to load booking details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (bookingId) fetchData();
  }, [bookingId]);

  const handleAdminOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideReason.trim()) {
      alert('A valid reason is required for administrative manual override.');
      return;
    }
    setOverrideSubmitting(true);
    try {
      await bookingsApi.override(bookingId, {
        resource_id: overrideResourceId,
        date: overrideDate,
        start_time: overrideStartTime,
        end_time: overrideEndTime,
        reason: overrideReason
      });
      setShowOverrideModal(false);
      setOverrideReason('');
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Override failed');
    } finally {
      setOverrideSubmitting(false);
    }
  };

  if (loading || !booking) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // Extract structured decision factors from trace if present
  let decisionFactors: StructuredDecisionFactors | null = null;
  const lastStep = trace?.steps?.slice(-1)[0];
  if (lastStep?.output_snapshot?.decision_factors) {
    decisionFactors = lastStep.output_snapshot.decision_factors as StructuredDecisionFactors;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link to="/my-bookings" className="flex items-center space-x-1.5 text-xs text-slate-500 hover:text-slate-800">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Bookings</span>
        </Link>
        {isAdminOrManager && (
          <button
            onClick={() => setShowOverrideModal(true)}
            className="px-3.5 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 font-semibold text-xs rounded-lg border border-purple-200 flex items-center space-x-1.5 transition-colors"
          >
            <Settings2 className="w-4 h-4 text-purple-600" />
            <span>Admin Manual Override</span>
          </button>
        )}
      </div>

      {/* Main Booking Summary Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-slate-900">{booking.event_name}</h1>
              <StatusBadge status={booking.status} />
              <PriorityBadge priority={booking.priority} />
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Requested by <span className="font-semibold text-slate-700">{booking.requester_name || 'Student'}</span> • {booking.department_name || 'General'}
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs bg-slate-100 px-3 py-1 rounded-md text-slate-600 font-mono">
              Booking #{booking.id}
            </span>
          </div>
        </div>

        {/* Key Attributes Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5 text-slate-400 font-bold uppercase text-[10px]">
              <Building2 className="w-3.5 h-3.5 text-blue-500" />
              <span>Allocated Resource</span>
            </div>
            <p className="text-sm font-bold text-slate-800 mt-1">
              {booking.resource_name || 'Pending AI Allocation'}
            </p>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5 text-slate-400 font-bold uppercase text-[10px]">
              <Calendar className="w-3.5 h-3.5 text-emerald-500" />
              <span>Scheduled Date</span>
            </div>
            <p className="text-sm font-bold text-slate-800 mt-1">{booking.date}</p>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5 text-slate-400 font-bold uppercase text-[10px]">
              <Clock className="w-3.5 h-3.5 text-amber-500" />
              <span>Time Slot</span>
            </div>
            <p className="text-sm font-bold text-slate-800 mt-1">{booking.start_time} - {booking.end_time}</p>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5 text-slate-400 font-bold uppercase text-[10px]">
              <Users className="w-3.5 h-3.5 text-purple-500" />
              <span>Attendees</span>
            </div>
            <p className="text-sm font-bold text-slate-800 mt-1">{booking.participant_count} participants</p>
          </div>
        </div>

        {/* Facilities & Raw Prompt */}
        <div className="pt-2 text-xs space-y-2">
          {booking.raw_request && (
            <div className="p-3 bg-blue-50/50 rounded-lg border border-blue-100 text-slate-700">
              <span className="font-semibold text-blue-900 block mb-0.5">Original Natural Language Request:</span>
              "{booking.raw_request}"
            </div>
          )}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="font-semibold text-slate-500 text-[11px] uppercase">Facilities:</span>
            {booking.equipment_needed?.map(eq => (
              <span key={eq} className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded border text-[11px]">
                {eq}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Decision Factors Card */}
      {decisionFactors && <DecisionFactorsCard factors={decisionFactors} />}

      {/* Multi-Agent Trace Pipeline */}
      {trace && (
        <AgentTraceViewer
          steps={trace.steps}
          totalTimeMs={trace.total_execution_time_ms}
        />
      )}

      {/* Admin Override Modal */}
      {showOverrideModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center space-x-2 text-purple-700 pb-2 border-b">
              <Settings2 className="w-5 h-5" />
              <h3 className="font-bold text-lg">Administrator Manual Override</h3>
            </div>

            <p className="text-xs text-slate-500">
              Manual interventions immediately update the allocation, calendar, and trigger an auditable decision log.
            </p>

            <form onSubmit={handleAdminOverride} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">Target Resource</label>
                <select
                  value={overrideResourceId}
                  onChange={(e) => setOverrideResourceId(Number(e.target.value))}
                  className="w-full p-2 bg-slate-50 border rounded-lg"
                >
                  {resources.map(r => (
                    <option key={r.id} value={r.id}>
                      {r.name} (Cap: {r.capacity})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Date</label>
                  <input
                    type="date"
                    required
                    value={overrideDate}
                    onChange={(e) => setOverrideDate(e.target.value)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Start Time</label>
                  <input
                    type="time"
                    required
                    value={overrideStartTime}
                    onChange={(e) => setOverrideStartTime(e.target.value)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">End Time</label>
                  <input
                    type="time"
                    required
                    value={overrideEndTime}
                    onChange={(e) => setOverrideEndTime(e.target.value)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">
                  Mandatory Reason for Override *
                </label>
                <textarea
                  required
                  rows={3}
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  placeholder="e.g. Dean's special approval for international delegation visit."
                  className="w-full p-2 bg-slate-50 border rounded-lg resize-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setShowOverrideModal(false)}
                  className="px-4 py-2 text-slate-500 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={overrideSubmitting}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow-sm"
                >
                  {overrideSubmitting ? 'Applying Override...' : 'Confirm Override'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
