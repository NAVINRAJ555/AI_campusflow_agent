import React, { useEffect, useState } from 'react';
import { resourcesApi } from '../services/api';
import { ResourceAvailability, Resource } from '../types';
import { Calendar, Clock, Building2, Users, CheckCircle, XCircle, AlertCircle, Wrench } from 'lucide-react';

export const ResourceAvailabilityPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState('2026-09-15');
  const [availabilities, setAvailabilities] = useState<ResourceAvailability[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [avRes, rList] = await Promise.all([
        resourcesApi.getAllAvailability(selectedDate),
        resourcesApi.getAll()
      ]);
      setAvailabilities(avRes.data);
      setResources(rList.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedDate]);

  const filteredAvail = availabilities.filter(a => {
    if (selectedType === 'ALL') return true;
    const r = resources.find(item => item.id === a.resource_id);
    return r?.resource_type === selectedType;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Resource Availability Matrix</h1>
          <p className="text-xs text-slate-500 mt-1">Real-time schedule inspection across all university facilities.</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm text-xs">
            <Calendar className="w-4 h-4 text-slate-400" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-transparent font-semibold text-slate-800 focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Resource Type Filter */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        {['ALL', 'seminar_hall', 'auditorium', 'smart_classroom', 'computer_lab', 'conference_room'].map(t => (
          <button
            key={t}
            onClick={() => setSelectedType(t)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
              selectedType === t
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {t === 'ALL' ? 'All Resources' : t.replace('_', ' ').toUpperCase()}
          </button>
        ))}
      </div>

      {/* Grid of Resource Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400 text-xs">
            Loading real-time availability...
          </div>
        ) : filteredAvail.length === 0 ? (
          <div className="col-span-full py-12 text-center text-slate-400 text-xs">
            No resources match the selected filter.
          </div>
        ) : (
          filteredAvail.map(a => {
            const rInfo = resources.find(r => r.id === a.resource_id);
            const totalBooked = a.booked_slots.length;

            return (
              <div
                key={a.resource_id}
                className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col justify-between hover:shadow-md transition-shadow"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-bold text-slate-900 text-sm">{a.resource_name}</h3>
                      <p className="text-[11px] text-slate-400 mt-0.5">{rInfo?.location || 'Campus Center'}</p>
                    </div>
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                        a.status === 'ACTIVE'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : 'bg-amber-50 text-amber-700 border-amber-200'
                      }`}
                    >
                      {a.status}
                    </span>
                  </div>

                  <div className="flex items-center space-x-4 mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600">
                    <div className="flex items-center space-x-1">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      <span>Cap: {rInfo?.capacity}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>{a.operating_start} - {a.operating_end}</span>
                    </div>
                  </div>

                  {/* Visual Day Time Slot Blocks */}
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-[11px] mb-1.5">
                      <span className="font-semibold text-slate-700">Scheduled Slots ({totalBooked})</span>
                      <span className="text-slate-400">{a.available_slots.length} open windows</span>
                    </div>

                    <div className="space-y-1.5">
                      {a.booked_slots.length === 0 ? (
                        <div className="p-2 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium flex items-center space-x-1.5">
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Fully available all day</span>
                        </div>
                      ) : (
                        a.booked_slots.map((slot, sIdx) => (
                          <div
                            key={sIdx}
                            className="p-2 bg-rose-50 border border-rose-100 rounded-lg text-xs flex items-center justify-between"
                          >
                            <span className="font-semibold text-rose-800">
                              {slot.start_time} - {slot.end_time}
                            </span>
                            <span className="text-rose-600 truncate max-w-[120px]">
                              {slot.event_name || 'Confirmed Booking'}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Equipment Tags */}
                <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap gap-1">
                  {rInfo?.equipment.map(eq => (
                    <span key={eq} className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px]">
                      {eq.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
