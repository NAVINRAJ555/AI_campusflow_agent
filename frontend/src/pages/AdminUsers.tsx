import React, { useEffect, useState } from 'react';
import { usersApi } from '../services/api';
import { User, UserRole } from '../types';
import { Users, Shield, Mail, Building, Trash2 } from 'lucide-react';

export const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await usersApi.getAll();
      setUsers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to remove this user account?')) {
      try {
        await usersApi.delete(id);
        fetchUsers();
      } catch (err) {
        alert('Failed to delete user');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
        <p className="text-xs text-slate-500 mt-1">Manage institutional users and role-based access permissions.</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Email</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Department</th>
                <th className="py-3 px-4">Registered</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">Loading user directory...</td>
                </tr>
              ) : users.map(u => (
                <tr key={u.id} className="hover:bg-slate-50/60">
                  <td className="py-3.5 px-4 font-bold text-slate-900">{u.name}</td>
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-600">{u.email}</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-50 text-blue-700 border border-blue-200">
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">{u.department_name || 'General'}</td>
                  <td className="py-3.5 px-4 text-slate-400">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => handleDelete(u.id)}
                      className="p-1 text-slate-400 hover:text-rose-600 rounded"
                      title="Delete User"
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
    </div>
  );
};
