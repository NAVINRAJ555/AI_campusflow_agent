import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { aiApi, bookingsApi } from '../services/api';
import {
  Sparkles,
  FileText,
  Clock,
  Calendar,
  Building2,
  Users,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  RotateCcw
} from 'lucide-react';

export const CreateBooking: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'structured' | 'natural'>('natural');

  // Natural language state
  const [prompt, setPrompt] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [extractedData, setExtractedData] = useState<any | null>(null);
  const [extractionReasoning, setExtractionReasoning] = useState<string | null>(null);

  // Structured form state
  const [eventName, setEventName] = useState('');
  const [eventType, setEventType] = useState('technical_event');
  const [resourceType, setResourceType] = useState('seminar_hall');
  const [preferredResource, setPreferredResource] = useState('Seminar Hall A');
  const [date, setDate] = useState('2026-09-15');
  const [startTime, setStartTime] = useState('10:00');
  const [endTime, setEndTime] = useState('13:00');
  const [participantCount, setParticipantCount] = useState(250);
  const [equipment, setEquipment] = useState<string[]>(['projector', 'microphone']);
  const [timeFlexible, setTimeFlexible] = useState(true);
  const [maxShiftMinutes, setMaxShiftMinutes] = useState(60);
  const [additionalRequirements, setAdditionalRequirements] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const demoPrompt =
    'I need Seminar Hall A tomorrow from 10 AM to 1 PM for 250 students for a CSE technical symposium. We need a projector and microphone. We can shift the event by one hour.';

  const handleUnderstand = async () => {
    if (!prompt.trim()) return;
    setIsAnalyzing(true);
    setError(null);
    setExtractedData(null);

    try {
      const res = await aiApi.understandRequest(prompt);
      if (res.data.success) {
        setExtractedData(res.data.data);
        setExtractionReasoning(res.data.reasoning);

        // Populate structured fields from extraction
        const d = res.data.data;
        if (d.event_name) setEventName(d.event_name);
        if (d.event_type) setEventType(d.event_type);
        if (d.resource_type) setResourceType(d.resource_type);
        if (d.preferred_resource) setPreferredResource(d.preferred_resource);
        if (d.date) setDate(d.date);
        if (d.start_time) setStartTime(d.start_time);
        if (d.end_time) setEndTime(d.end_time);
        if (d.participant_count) setParticipantCount(d.participant_count);
        if (d.equipment) setEquipment(d.equipment);
        if (d.flexibility) {
          setTimeFlexible(d.flexibility.time_flexible);
          setMaxShiftMinutes(d.flexibility.max_shift_minutes);
        }
      } else {
        setError('Could not extract structured data. Please verify your prompt or use the structured form.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'AI parser error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleEquipmentToggle = (item: string) => {
    if (equipment.includes(item)) {
      setEquipment(equipment.filter(e => e !== item));
    } else {
      setEquipment([...equipment, item]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const payload = {
      event_name: eventName,
      event_type: eventType,
      resource_type: resourceType,
      preferred_resource: preferredResource,
      date,
      start_time: startTime,
      end_time: endTime,
      participant_count: Number(participantCount),
      equipment,
      flexibility: {
        time_flexible: timeFlexible,
        max_shift_minutes: Number(maxShiftMinutes),
        alternative_dates: []
      },
      additional_requirements: additionalRequirements,
      raw_request: activeTab === 'natural' ? prompt : `Structured booking for ${eventName}`
    };

    try {
      const res = await bookingsApi.create(payload, true);
      // Navigate to booking details / trace
      navigate(`/bookings/${res.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit booking request.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Create Resource Booking</h1>
        <p className="text-xs text-slate-500 mt-1">
          Submit your university resource request via Natural Language AI or structured scheduling form.
        </p>
      </div>

      {/* Method Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          type="button"
          onClick={() => setActiveTab('natural')}
          className={`flex items-center space-x-2 py-3 px-5 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'natural'
              ? 'border-blue-600 text-blue-600 bg-blue-50/50'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Method 2: Natural Language AI</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('structured')}
          className={`flex items-center space-x-2 py-3 px-5 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'structured'
              ? 'border-blue-600 text-blue-600 bg-blue-50/50'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Method 1: Structured Form</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* METHOD 2: Natural Language Tab */}
      {activeTab === 'natural' && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Describe Your Event in Plain English
              </label>
              <button
                type="button"
                onClick={() => setPrompt(demoPrompt)}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center space-x-1"
              >
                <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                <span>Insert Demo Scenario Prompt</span>
              </button>
            </div>

            <textarea
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. I need Seminar Hall A tomorrow from 10 AM to 1 PM for 250 students for a CSE technical symposium. We need a projector and microphone. We can shift the event by one hour."
              className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white resize-none"
            />

            <div className="flex justify-end">
              <button
                type="button"
                onClick={handleUnderstand}
                disabled={isAnalyzing || !prompt.trim()}
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-blue-500/20 flex items-center space-x-2 disabled:opacity-50 transition-all"
              >
                {isAnalyzing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>AI is understanding your request...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Understand & Extract Request</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* AI Extracted Review Card (Section 10 Requirement) */}
          {extractedData && (
            <div className="bg-gradient-to-br from-white to-blue-50/40 rounded-2xl border-2 border-blue-200 shadow-md p-6 space-y-5 animate-in fade-in slide-in-from-bottom-2 duration-200">
              <div className="flex items-center justify-between pb-3 border-b border-blue-100">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                  <h3 className="font-bold text-slate-900 text-base">Request Understanding Verification</h3>
                </div>
                <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2.5 py-0.5 rounded-full">
                  Extracted & Validated
                </span>
              </div>

              <p className="text-xs text-slate-600 italic">
                {extractionReasoning || 'Please review the extracted booking parameters before confirming.'}
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                  <span className="text-slate-400 font-bold uppercase text-[10px]">Event Name</span>
                  <div className="font-semibold text-slate-800 mt-0.5">{eventName}</div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                  <span className="text-slate-400 font-bold uppercase text-[10px]">Preferred Resource</span>
                  <div className="font-semibold text-slate-800 mt-0.5">{preferredResource}</div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                  <span className="text-slate-400 font-bold uppercase text-[10px]">Date & Time</span>
                  <div className="font-semibold text-slate-800 mt-0.5">{date} ({startTime} - {endTime})</div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                  <span className="text-slate-400 font-bold uppercase text-[10px]">Participants</span>
                  <div className="font-semibold text-slate-800 mt-0.5">{participantCount} students</div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                  <span className="text-slate-400 font-bold uppercase text-[10px]">Equipment</span>
                  <div className="font-semibold text-slate-800 mt-0.5">{equipment.join(', ') || 'None'}</div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                  <span className="text-slate-400 font-bold uppercase text-[10px]">Time Flexibility</span>
                  <div className="font-semibold text-slate-800 mt-0.5">
                    {timeFlexible ? `Flexible (±${maxShiftMinutes} mins)` : 'Fixed Timing'}
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-blue-100 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setActiveTab('structured')}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-900"
                >
                  Edit details in structured form →
                </button>
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm rounded-xl shadow-md shadow-emerald-600/30 flex items-center space-x-2"
                >
                  <span>{isSubmitting ? 'Submitting to AI Pipeline...' : 'Confirm & Run Scheduling Pipeline'}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* METHOD 1: Structured Form Tab */}
      {activeTab === 'structured' && (
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Event Name *
              </label>
              <input
                type="text"
                required
                value={eventName}
                onChange={(e) => setEventName(e.target.value)}
                placeholder="e.g. CSE Technical Symposium"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Event Type *
              </label>
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              >
                <option value="technical_event">Technical Symposium / Hackathon (HIGH)</option>
                <option value="placement_drive">Placement Activity (VERY_HIGH)</option>
                <option value="exam">Official Examination (VERY_HIGH)</option>
                <option value="department_seminar">Department Seminar (MEDIUM)</option>
                <option value="club_meeting">Student Club Meeting (LOW)</option>
                <option value="administrative">Administrative Event (MEDIUM)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Resource Type
              </label>
              <select
                value={resourceType}
                onChange={(e) => setResourceType(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              >
                <option value="seminar_hall">Seminar Hall</option>
                <option value="auditorium">Auditorium</option>
                <option value="smart_classroom">Smart Classroom</option>
                <option value="computer_lab">Computer Lab</option>
                <option value="conference_room">Conference Room</option>
                <option value="bus">Campus Bus</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Preferred Resource
              </label>
              <select
                value={preferredResource}
                onChange={(e) => setPreferredResource(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              >
                <option value="Seminar Hall A">Seminar Hall A (Cap: 300)</option>
                <option value="Seminar Hall B">Seminar Hall B (Cap: 300)</option>
                <option value="Main Auditorium">Main Auditorium (Cap: 800)</option>
                <option value="Smart Classroom 1">Smart Classroom 1 (Cap: 75)</option>
                <option value="Smart Classroom 2">Smart Classroom 2 (Cap: 75)</option>
                <option value="Computer Lab 1">Computer Lab 1 (Cap: 60)</option>
                <option value="Computer Lab 2">Computer Lab 2 (Cap: 60)</option>
                <option value="Conference Room A">Conference Room A (Cap: 40)</option>
                <option value="Conference Room B">Conference Room B (Cap: 40)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Participant Count *
              </label>
              <input
                type="number"
                required
                min={1}
                value={participantCount}
                onChange={(e) => setParticipantCount(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Date *
              </label>
              <input
                type="date"
                required
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Start Time *
              </label>
              <input
                type="time"
                required
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                End Time *
              </label>
              <input
                type="time"
                required
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              />
            </div>
          </div>

          {/* Equipment Checkboxes */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              Equipment Requirements
            </label>
            <div className="flex flex-wrap gap-2">
              {['projector', 'microphone', 'sound_system', 'video_conferencing', 'computers', 'smart_board'].map(eq => (
                <button
                  type="button"
                  key={eq}
                  onClick={() => handleEquipmentToggle(eq)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    equipment.includes(eq)
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {eq.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Scheduling Flexibility */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase text-slate-800">Time Shift Flexibility</span>
                <p className="text-xs text-slate-500">Allow Negotiation Agent to shift timing if conflicts arise</p>
              </div>
              <input
                type="checkbox"
                checked={timeFlexible}
                onChange={(e) => setTimeFlexible(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
            </div>

            {timeFlexible && (
              <div className="flex items-center space-x-3 pt-2">
                <span className="text-xs text-slate-600">Maximum shift allowable:</span>
                <select
                  value={maxShiftMinutes}
                  onChange={(e) => setMaxShiftMinutes(Number(e.target.value))}
                  className="px-2.5 py-1 bg-white border border-slate-200 rounded text-xs"
                >
                  <option value={30}>± 30 Minutes</option>
                  <option value={60}>± 60 Minutes (1 Hour)</option>
                  <option value={120}>± 120 Minutes (2 Hours)</option>
                </select>
              </div>
            )}
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md shadow-blue-500/25 flex items-center space-x-2"
            >
              <span>{isSubmitting ? 'Processing AI Pipeline...' : 'Submit Booking Request'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
