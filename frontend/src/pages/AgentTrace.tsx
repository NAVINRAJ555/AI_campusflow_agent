import React, { useEffect, useState } from 'react';
import { bookingsApi, schedulingApi } from '../services/api';
import { Booking, AgentTraceResponse } from '../types';
import { AgentTraceViewer } from '../components/AgentTraceViewer';
import { DecisionFactorsCard } from '../components/DecisionFactorsCard';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { BrainCircuit, Search } from 'lucide-react';

export const AgentTracePage: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [selectedBookingId, setSelectedBookingId] = useState<number | null>(null);
  const [trace, setTrace] = useState<AgentTraceResponse | null>(null);
  const [loadingTrace, setLoadingTrace] = useState(false);

  useEffect(() => {
    bookingsApi.getAll().then(res => {
      setBookings(res.data);
      if (res.data.length > 0) {
        setSelectedBookingId(res.data[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedBookingId) {
      setLoadingTrace(true);
      schedulingApi.getAgentTrace(selectedBookingId)
        .then(res => setTrace(res.data))
        .catch(console.error)
        .finally(() => setLoadingTrace(false));
    }
  }, [selectedBookingId]);

  const selectedBooking = bookings.find(b => b.id === selectedBookingId);

  // Extract decision factors if present
  let factors = null;
  const lastStep = trace?.steps?.slice(-1)[0];
  if (lastStep?.output_snapshot?.decision_factors) {
    factors = lastStep.output_snapshot.decision_factors;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <div className="flex items-center space-x-2">
          <BrainCircuit className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-slate-900">Multi-Agent Decision Trace</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Inspect full transparency telemetry and explainability factors across the six autonomous scheduling agents.
        </p>
      </div>

      {/* Booking Selector Dropdown */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
        <label className="text-xs font-bold uppercase text-slate-500 shrink-0">Select Booking Request:</label>
        <select
          value={selectedBookingId || ''}
          onChange={(e) => setSelectedBookingId(Number(e.target.value))}
          className="w-full max-w-md p-2 bg-slate-50 border rounded-lg text-xs font-medium text-slate-800"
        >
          {bookings.map(b => (
            <option key={b.id} value={b.id}>
              #{b.id} - {b.event_name} ({b.date} • {b.status})
            </option>
          ))}
        </select>
      </div>

      {selectedBooking && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-slate-900">{selectedBooking.event_name}</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Requested venue: {selectedBooking.resource_name || selectedBooking.resource_type} • Date: {selectedBooking.date} ({selectedBooking.start_time} - {selectedBooking.end_time})
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <PriorityBadge priority={selectedBooking.priority} />
            <StatusBadge status={selectedBooking.status} />
          </div>
        </div>
      )}

      {loadingTrace ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading multi-agent execution steps...</div>
      ) : trace && trace.steps.length > 0 ? (
        <div className="space-y-6">
          {factors && <DecisionFactorsCard factors={factors} />}
          <AgentTraceViewer steps={trace.steps} totalTimeMs={trace.total_execution_time_ms} />
        </div>
      ) : (
        <div className="bg-white p-12 text-center text-xs text-slate-400 rounded-xl border">
          No agent trace logged for this booking yet.
        </div>
      )}
    </div>
  );
};
