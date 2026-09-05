import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { LogIn, Sparkles, UserCheck } from 'lucide-react';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('Password123!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 border border-slate-100">
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-blue-600 text-white font-black text-2xl flex items-center justify-center mx-auto shadow-lg shadow-blue-500/30">
            CF
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mt-3">Welcome to CampusFlow</h2>
          <p className="text-xs text-slate-500 mt-1">Autonomous University Resource Scheduling Framework</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@campusflow.edu"
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-lg shadow-md shadow-blue-600/30 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            <LogIn className="w-4 h-4" />
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
          </button>
        </form>

        {/* Demo Quick Logins */}
        <div className="mt-6 pt-6 border-t border-slate-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Demo Role Quick Access</span>
            <span className="text-[10px] text-blue-600 font-semibold flex items-center">
              <Sparkles className="w-3 h-3 mr-0.5" /> 1-Click Fill
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickLogin('student@campusflow.edu')}
              className="p-2 bg-slate-50 hover:bg-blue-50 hover:text-blue-700 text-slate-700 rounded-lg border border-slate-200 text-left transition-colors"
            >
              <div className="font-semibold">Student</div>
              <div className="text-[10px] text-slate-400 truncate">student@...</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('faculty@campusflow.edu')}
              className="p-2 bg-slate-50 hover:bg-blue-50 hover:text-blue-700 text-slate-700 rounded-lg border border-slate-200 text-left transition-colors"
            >
              <div className="font-semibold">Faculty</div>
              <div className="text-[10px] text-slate-400 truncate">faculty@...</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('deptadmin@campusflow.edu')}
              className="p-2 bg-slate-50 hover:bg-blue-50 hover:text-blue-700 text-slate-700 rounded-lg border border-slate-200 text-left transition-colors"
            >
              <div className="font-semibold">Dept Admin</div>
              <div className="text-[10px] text-slate-400 truncate">deptadmin@...</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('manager@campusflow.edu')}
              className="p-2 bg-slate-50 hover:bg-blue-50 hover:text-blue-700 text-slate-700 rounded-lg border border-slate-200 text-left transition-colors"
            >
              <div className="font-semibold">Resource Mgr</div>
              <div className="text-[10px] text-slate-400 truncate">manager@...</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('admin@campusflow.edu')}
              className="col-span-2 p-2 bg-purple-50 hover:bg-purple-100 text-purple-800 rounded-lg border border-purple-200 text-left transition-colors"
            >
              <div className="font-semibold flex items-center justify-between">
                <span>System Administrator</span>
                <span className="text-[10px] bg-purple-200 px-1.5 py-0.5 rounded">Full Control</span>
              </div>
              <div className="text-[10px] text-purple-500 truncate">admin@campusflow.edu</div>
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 font-semibold hover:underline">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
};
