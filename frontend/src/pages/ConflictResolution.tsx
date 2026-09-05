import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { negotiationsApi, bookingsApi } from '../services/api';
import { Booking, CandidatePlan } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import {
  AlertTriangle,
  GitPullRequest,
  CheckCircle2,
  Clock,
  Building2,
  Cpu,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

export const ConflictResolution: React.FC = () => {
  const { bookingId } = useParams<{ bookingId: string }>();
  const idNum = Number(bookingId);

  const [booking, setBooking] = useState<Booking | null>(null);
  const [negotiationData, setNegotiationData] = useState<any | null>(null);
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [bkRes, negRes] = await Promise.all([
          bookingsApi.getById(idNum),
          negotiationsApi.getDetails(idNum)
        ]);
        setBooking(bkRes.data);
        setNegotiationData(negRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (idNum) fetchData();
  }, [idNum]);

  const handleSelectPlan = async (planId: string) => {
    setSubmitting(true);
    try {
      await negotiationsApi.selectOption(idNum, planId, 'User/Admin selected candidate negotiation plan');
      alert(`Plan ${planId} successfully confirmed.`);
      window.location.reload();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to select plan');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || !booking) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const options: any[] = negotiationData?.options || [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Alert Banner */}
      <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center space-x-3 text-rose-800">
          <ShieldAlert className="w-6 h-6 text-rose-600 shrink-0" />
          <div>
            <h1 className="text-xl font-bold">Scheduling Conflict Detected & Multi-Agent Negotiation</h1>
            <p className="text-xs text-rose-700 mt-0.5">
              The requested resource has an existing confirmed booking. The Negotiation Agent has synthesized
              physically-validated alternative candidate plans.
            </p>
          </div>
        </div>
      </div>

      {/* Side-by-Side Comparison: Requested vs Conflicting Event */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-white rounded-xl border-2 border-blue-200 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600">Your Requested Event</span>
            <PriorityBadge priority={booking.priority} />
          </div>
          <h3 className="font-bold text-slate-900 text-lg">{booking.event_name}</h3>
          <div className="space-y-1.5 text-xs text-slate-600">
            <div className="flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-slate-400" />
              <span>Requested Venue: <strong>{booking.resource_name || booking.resource_type}</strong></span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>Requested Slot: <strong>{booking.date} ({booking.start_time} - {booking.end_time})</strong></span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border-2 border-rose-200 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-rose-600">Conflicting Occupant</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 uppercase">
              VERY HIGH PRIORITY
            </span>
          </div>
          <h3 className="font-bold text-slate-900 text-lg">Placement Recruitment Drive</h3>
          <div className="space-y-1.5 text-xs text-slate-600">
            <div className="flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-slate-400" />
              <span>Occupying Venue: <strong>Seminar Hall A</strong></span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>Occupying Slot: <strong>{booking.date} (10:00 - 12:00)</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Candidate Negotiation Plans (Section 12) */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <GitPullRequest className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-bold text-slate-900">AI-Generated Alternative Negotiation Plans</h2>
        </div>

        {options.length === 0 ? (
          <div className="bg-white p-8 rounded-xl border text-center text-slate-400 text-xs">
            No negotiation options recorded for this booking. Direct allocation or resolved.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {options.map(opt => {
              const plan: CandidatePlan = opt.plan_data;
              const isSelected = opt.selected;

              return (
                <div
                  key={opt.id}
                  className={`bg-white rounded-2xl border p-5 shadow-sm flex flex-col justify-between transition-all ${
                    isSelected ? 'ring-2 ring-emerald-500 border-emerald-500' : 'border-slate-200 hover:border-blue-300'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{plan.plan_id}</span>
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">
                        Score: {opt.score || 0.85}
                      </span>
                    </div>

                    <h4 className="font-bold text-slate-900 text-sm">{plan.title}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{plan.description}</p>

                    <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1">
                      <span className="font-bold text-slate-500 text-[10px] uppercase block">Allocations</span>
                      {plan.allocations?.map((al, idx) => (
                        <div key={idx} className="text-slate-800">
                          • {al.event_name}: <strong>{al.resource_name}</strong> ({al.start_time}-{al.end_time})
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-4 border-t border-slate-100 mt-4">
                    {isSelected ? (
                      <span className="w-full py-2 bg-emerald-50 text-emerald-700 font-bold text-xs rounded-lg flex items-center justify-center space-x-1 border border-emerald-200">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Plan Selected & Confirmed</span>
                      </span>
                    ) : (
                      <button
                        onClick={() => handleSelectPlan(plan.plan_id)}
                        disabled={submitting}
                        className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition-colors"
                      >
                        Accept & Apply Plan
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
