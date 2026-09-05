import React, { useEffect, useState } from 'react';
import { calendarApi, resourcesApi, usersApi } from '../services/api';
import { CalendarEventItem, Resource, Department } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { Calendar as CalendarIcon, Filter, Building2, Clock, Users, ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const CalendarView: React.FC = () => {
  const [events, setEvents] = useState<CalendarEventItem[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedDate, setSelectedDate] = useState('2026-09-15');
  const [selectedResource, setSelectedResource] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const res = await calendarApi.getEvents({
        date: selectedDate || undefined,
        resource_id: selectedResource ? Number(selectedResource) : undefined,
        resource_type: selectedType || undefined,
        department_id: selectedDepartment ? Number(selectedDepartment) : undefined,
        status: selectedStatus || undefined
      });
      setEvents(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    Promise.all([resourcesApi.getAll(), usersApi.getDepartments()])
      .then(([rRes, dRes]) => {
        setResources(rRes.data);
        setDepartments(dRes.data);
      });
  }, []);

  useEffect(() => {
    fetchEvents();
  }, [selectedDate, selectedResource, selectedType, selectedDepartment, selectedStatus]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">University Campus Calendar</h1>
          <p className="text-xs text-slate-500 mt-1">Cross-department scheduled events and resource allocations.</p>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm text-xs">
            <CalendarIcon className="w-4 h-4 text-slate-400" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-transparent font-semibold text-slate-800 focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Multi-Dimensional Filter Bar (Section 20) */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div>
          <label className="block font-semibold text-slate-500 mb-1">Resource</label>
          <select
            value={selectedResource}
            onChange={(e) => setSelectedResource(e.target.value)}
            className="w-full p-2 bg-slate-50 border rounded-lg"
          >
            <option value="">All Venues</option>
            {resources.map(r => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-semibold text-slate-500 mb-1">Resource Type</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full p-2 bg-slate-50 border rounded-lg"
          >
            <option value="">All Types</option>
            <option value="seminar_hall">Seminar Hall</option>
            <option value="auditorium">Auditorium</option>
            <option value="smart_classroom">Smart Classroom</option>
            <option value="computer_lab">Computer Lab</option>
            <option value="conference_room">Conference Room</option>
          </select>
        </div>

        <div>
          <label className="block font-semibold text-slate-500 mb-1">Department</label>
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="w-full p-2 bg-slate-50 border rounded-lg"
          >
            <option value="">All Departments</option>
            {departments.map(d => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-semibold text-slate-500 mb-1">Booking Status</label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full p-2 bg-slate-50 border rounded-lg"
          >
            <option value="">All Statuses</option>
            <option value="APPROVED">Approved</option>
            <option value="RESCHEDULED">Rescheduled</option>
          </select>
        </div>
      </div>

      {/* Events Stream / Cards */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <span className="font-bold text-slate-800 text-sm">
            Scheduled Events on {selectedDate || 'All Dates'} ({events.length})
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading events...</div>
        ) : events.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">No scheduled events found for this filter.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {events.map(ev => (
              <div
                key={ev.id}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 hover:border-blue-300 transition-all flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between">
                    <h3 className="font-bold text-slate-900 text-sm">{ev.event_name}</h3>
                    <StatusBadge status={ev.status} size="sm" />
                  </div>

                  <div className="space-y-1 text-xs text-slate-600">
                    <div className="flex items-center space-x-1.5 font-medium text-slate-800">
                      <Building2 className="w-3.5 h-3.5 text-blue-500" />
                      <span>{ev.resource_name} ({ev.resource_type})</span>
                    </div>
                    <div className="flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-amber-500" />
                      <span>{ev.date} • {ev.start_time} - {ev.end_time}</span>
                    </div>
                    <div className="flex items-center space-x-1.5">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      <span>{ev.department_name}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 mt-3 border-t border-slate-200/60 flex items-center justify-between">
                  <PriorityBadge priority={ev.priority} />
                  <Link
                    to={`/bookings/${ev.booking_id}`}
                    className="text-xs font-semibold text-blue-600 hover:underline"
                  >
                    View Agent Trace →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
