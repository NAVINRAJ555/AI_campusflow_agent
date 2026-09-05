import React, { useEffect, useState } from 'react';
import { bookingsApi } from '../services/api';
import { Booking, BookingStatus } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { Link } from 'react-router-dom';
import { Search, Filter, CalendarDays, ArrowRight, XCircle } from 'lucide-react';

export const MyBookings: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const res = await bookingsApi.getAll();
      setBookings(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleCancel = async (id: number) => {
    if (window.confirm('Are you sure you want to cancel this booking?')) {
      try {
        await bookingsApi.cancel(id);
        fetchBookings();
      } catch (err) {
        alert('Failed to cancel booking');
      }
    }
  };

  const filtered = bookings.filter(b => {
    const matchesStatus = statusFilter === 'ALL' || b.status === statusFilter;
    const matchesQuery =
      b.event_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (b.resource_name && b.resource_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesStatus && matchesQuery;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Resource Bookings</h1>
          <p className="text-xs text-slate-500 mt-1">Review active, negotiated, and completed university reservations.</p>
        </div>
        <Link
          to="/create-booking"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-sm transition-all text-center"
        >
          + New Booking
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search event or venue..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center space-x-2 overflow-x-auto w-full sm:w-auto">
          {['ALL', 'APPROVED', 'PROCESSING', 'CONFLICT', 'RESCHEDULED', 'REJECTED', 'CANCELLED'].map(s => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                statusFilter === s
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Bookings Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Event Details</th>
                <th className="py-3 px-4">Allocated Venue</th>
                <th className="py-3 px-4">Date & Time</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">Loading bookings...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">No bookings match criteria</td>
                </tr>
              ) : (
                filtered.map(b => (
                  <tr key={b.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900 text-sm">{b.event_name}</div>
                      <div className="text-[11px] text-slate-500">
                        {b.participant_count} attendees • {b.requester_name || 'Requester'}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {b.resource_name || b.resource_type}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-medium text-slate-800">{b.date}</div>
                      <div className="text-[10px] text-slate-400">{b.start_time} - {b.end_time}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <PriorityBadge priority={b.priority} />
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={b.status} />
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <Link
                        to={`/bookings/${b.id}`}
                        className="px-2.5 py-1 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold rounded-md transition-colors"
                      >
                        Trace & Details
                      </Link>
                      {b.status !== 'CANCELLED' && b.status !== 'REJECTED' && (
                        <button
                          onClick={() => handleCancel(b.id)}
                          className="px-2 py-1 text-slate-400 hover:text-rose-600 rounded"
                          title="Cancel Booking"
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
