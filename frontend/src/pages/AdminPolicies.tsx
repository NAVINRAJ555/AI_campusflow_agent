import React, { useEffect, useState } from 'react';
import { policiesApi } from '../services/api';
import { Policy, PriorityLevel } from '../types';
import { Shield, Plus, Edit, Trash2, CheckCircle2, ToggleLeft, ToggleRight } from 'lucide-react';
import { PriorityBadge } from '../components/PriorityBadge';

export const AdminPolicies: React.FC = () => {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [ruleType, setRuleType] = useState('PRIORITY_ELEVATION');
  const [ruleConfig, setRuleConfig] = useState('{"event_types": ["symposium"], "elevate_to": "HIGH"}');
  const [priority, setPriority] = useState<PriorityLevel>('HIGH');
  const [active, setActive] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const res = await policiesApi.getAll();
      setPolicies(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleToggleActive = async (p: Policy) => {
    try {
      await policiesApi.update(p.id, { active: !p.active });
      fetchPolicies();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Delete this institutional policy?')) {
      try {
        await policiesApi.delete(id);
        fetchPolicies();
      } catch (err) {
        alert('Failed to delete policy');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await policiesApi.create({
        name,
        description,
        rule_type: ruleType,
        rule_config: ruleConfig,
        priority,
        active
      });
      setShowModal(false);
      setName('');
      setDescription('');
      fetchPolicies();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create policy');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Institutional Policy Engine</h1>
          <p className="text-xs text-slate-500 mt-1">
            Dynamic database-driven university scheduling rules evaluated in real-time by Policy & Priority Agent.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center space-x-1.5 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Policy Rule</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400 text-xs">Loading policies...</div>
        ) : policies.map(p => (
          <div
            key={p.id}
            className={`bg-white rounded-2xl border p-5 shadow-sm space-y-3 transition-all ${
              p.active ? 'border-slate-200' : 'border-slate-200 bg-slate-50/50 opacity-60'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-2">
                <Shield className={`w-5 h-5 ${p.active ? 'text-blue-600' : 'text-slate-400'}`} />
                <h3 className="font-bold text-slate-900 text-sm">{p.name}</h3>
              </div>
              <PriorityBadge priority={p.priority} />
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">{p.description}</p>

            <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1 font-mono text-[11px] border border-slate-100">
              <div className="text-slate-500 font-sans font-bold text-[10px] uppercase">Rule Type: {p.rule_type}</div>
              <div className="text-slate-800 break-all">{p.rule_config}</div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={() => handleToggleActive(p)}
                className={`text-xs font-semibold flex items-center space-x-1 ${
                  p.active ? 'text-emerald-700' : 'text-slate-500'
                }`}
              >
                {p.active ? (
                  <>
                    <ToggleRight className="w-5 h-5 text-emerald-600" />
                    <span>Active Policy</span>
                  </>
                ) : (
                  <>
                    <ToggleLeft className="w-5 h-5 text-slate-400" />
                    <span>Inactive</span>
                  </>
                )}
              </button>

              <button
                onClick={() => handleDelete(p.id)}
                className="p-1.5 text-slate-400 hover:text-rose-600 rounded"
                title="Delete Policy"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="font-bold text-slate-900 text-lg">Create University Policy</h3>

            <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">Policy Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Hackathon Weekend Priority"
                  className="w-full p-2 bg-slate-50 border rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">Description *</label>
                <textarea
                  required
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Explains what this rule does"
                  className="w-full p-2 bg-slate-50 border rounded-lg resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Rule Type</label>
                  <select
                    value={ruleType}
                    onChange={(e) => setRuleType(e.target.value)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  >
                    <option value="PRIORITY_ELEVATION">Priority Elevation</option>
                    <option value="CAPACITY_CHECK">Capacity Enforcement</option>
                    <option value="OPERATING_HOURS">Operating Hours Compliance</option>
                    <option value="DEPARTMENT_RESTRICTION">Department Restriction</option>
                    <option value="ADVANCE_BOOKING">Advance Notice Window</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold uppercase text-slate-700 mb-1">Policy Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as PriorityLevel)}
                    className="w-full p-2 bg-slate-50 border rounded-lg"
                  >
                    <option value="VERY_HIGH">Very High</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold uppercase text-slate-700 mb-1">
                  Rule Config (JSON) *
                </label>
                <textarea
                  required
                  rows={3}
                  value={ruleConfig}
                  onChange={(e) => setRuleConfig(e.target.value)}
                  className="w-full p-2 bg-slate-900 text-emerald-400 font-mono text-[11px] rounded-lg resize-none"
                />
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  checked={active}
                  onChange={(e) => setActive(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-slate-700 font-medium">Activate immediately</span>
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
                  {submitting ? 'Creating...' : 'Save Policy'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
