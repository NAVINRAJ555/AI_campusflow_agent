import React, { useEffect, useState } from 'react';
import { resourcesApi } from '../services/api';
import { Resource, ResourceStatus } from '../types';
import { Building2, Plus, Edit, Trash2, CheckCircle, Wrench, XCircle } from 'lucide-react';

export const AdminResources: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal form state
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [name, setName] = useState('');
  const [resourceType, setResourceType] = useState('seminar_hall');
  const [location, setLocation] = useState('');
  const [capacity, setCapacity] = useState(100);
  const [operatingStart, setOperatingStart] = useState('08:00');
  const [operatingEnd, setOperatingEnd] = useState('20:00');
  const [status, setStatus] = useState<ResourceStatus>('ACTIVE');
  const [equipmentStr, setEquipmentStr] = useState('projector, microphone');
  const [submitting, setSubmitting] = useState(false);

  const fetchResources = async () => {
    setLoading(true);
    try {
      const res = await resourcesApi.getAll();
      setResources(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, []);

  const openCreateModal = () => {
    setEditingId(null);
    setName('');
    setResourceType('seminar_hall');
    setLocation('');
    setCapacity(100);
    setOperatingStart('08:00');
    setOperatingEnd('20:00');
    setStatus('ACTIVE');
    setEquipmentStr('projector, microphone');
    setShowModal(true);
  };

  const openEditModal = (r: Resource) => {
    setEditingId(r.id);
    setName(r.name);
    setResourceType(r.resource_type);
    setLocation(r.location);
    setCapacity(r.capacity);
    setOperatingStart(r.operating_start);
    setOperatingEnd(r.operating_end);
    setStatus(r.status);
    setEquipmentStr(r.equipment.join(', '));
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this resource?')) {
      try {
        await resourcesApi.delete(id);
        fetchResources();
      } catch (err) {
        alert('Failed to delete resource');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    const equipArray = equipmentStr.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);

    const payload = {
      name,
      resource_type: resourceType,
      location,
      capacity: Number(capacity),
      operating_start: operatingStart,
      operating_end: operatingEnd,
      status,
      equipment: equipArray
    };

    try {
      if (editingId) {
        await resourcesApi.update(editingId, payload);
      } else {
        await resourcesApi.create(payload);
      }
      setShowModal(false);
      fetchResources();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Operation failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Resource Management</h1>
          <p className="text-xs text-slate-500 mt-1">Configure campus auditoriums, seminar halls, smart rooms, and labs.</p>
        </div>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center space-x-1.5 self-start transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Add Resource</span>
        </button>
      </div>

      {/* Resources Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Resource Name</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Capacity</th>
                <th className="py-3 px-4">Operating Hours</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Equipment</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">Loading resources...</td>
                </tr>
              ) : resources.map(r => (
                <tr key={r.id} className="hover:bg-slate-50/60">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-900">{r.name}</div>
                    <div className="text-[11px] text-slate-400">{r.location}</div>
                  </td>
                  <td className="py-3.5 px-4 capitalize font-medium">{r.resource_type.replace('_', ' ')}</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-800">{r.capacity} seats</td>
                  <td className="py-3.5 px-4">{r.operating_start} - {r.operating_end}</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      r.status === 'ACTIVE'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 max-w-xs truncate">
                    {r.equipment.join(', ')}
                  </td>
                  <td className="py-3.5 px-4 text-right space-x-2">
                    <button
                      onClick={() => openEditModal(r)}
                      className="p-1 text-slate-500 hover:text-blue-600 rounded"
                      title="Edit Resource"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(r.id)}
                      className="p-1 text-slate-500 hover:text-rose-600 rounded"
                      title="Delete Resource"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="font-bold text-slate-900 text-lg">
              {editingId ? 'Edit Resource' : 'Create New Resource'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">Resource Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Smart Classroom 3"
                  className="w-full p-2 bg-slate-50 border rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Type</label>
                  <select
                    value={resourceType}
                    onChange={(e) => setResourceType(e.target.value)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
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
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Capacity</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={capacity}
                    onChange={(e) => setCapacity(Number(e.target.value))}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">Location</label>
                <input
                  type="text"
                  required
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Engineering Block 2, Room 301"
                  className="w-full p-2 bg-slate-50 border rounded-lg"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Opens</label>
                  <input
                    type="time"
                    required
                    value={operatingStart}
                    onChange={(e) => setOperatingStart(e.target.value)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Closes</label>
                  <input
                    type="time"
                    required
                    value={operatingEnd}
                    onChange={(e) => setOperatingEnd(e.target.value)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value as ResourceStatus)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  >
                    <option value="ACTIVE">Active</option>
                    <option value="MAINTENANCE">Maintenance</option>
                    <option value="INACTIVE">Inactive</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">
                  Equipment (comma-separated)
                </label>
                <input
                  type="text"
                  value={equipmentStr}
                  onChange={(e) => setEquipmentStr(e.target.value)}
                  placeholder="projector, microphone, sound_system"
                  className="w-full p-2 bg-slate-50 border rounded-lg"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-slate-500 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-sm"
                >
                  {submitting ? 'Saving...' : 'Save Resource'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
