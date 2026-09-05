import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Bell, LogOut, User, Check, Sparkles } from 'lucide-react';
import { notificationsApi } from '../services/api';
import { NotificationItem } from '../types';
import { Link, useNavigate } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifMenu, setShowNotifMenu] = useState(false);

  useEffect(() => {
    if (user) {
      notificationsApi.getAll()
        .then(res => setNotifications(res.data))
        .catch(() => {});
    }
  }, [user]);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const markAllRead = async () => {
    for (const n of notifications.filter(n => !n.is_read)) {
      await notificationsApi.markRead(n.id);
    }
    setNotifications(notifications.map(n => ({ ...n, is_read: true })));
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 sticky top-0 z-30 px-6 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <Link to="/" className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-700 via-blue-600 to-indigo-500 flex items-center justify-center text-white font-black text-lg shadow-md shadow-blue-500/20">
            CF
          </div>
          <div>
            <span className="font-bold text-lg text-slate-900 tracking-tight">Campus<span className="text-blue-600">Flow</span></span>
            <span className="hidden sm:inline-block ml-2 text-[10px] font-semibold uppercase tracking-wider bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full border border-blue-100">
              Agentic AI v1.0
            </span>
          </div>
        </Link>
      </div>

      <div className="flex items-center space-x-4">
        {/* Notification Bell Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifMenu(!showNotifMenu)}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 relative transition-colors"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-rose-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center animate-pulse">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifMenu && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-4 py-2 border-b border-slate-100 flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-600">Notifications</span>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-[11px] text-blue-600 hover:underline flex items-center space-x-1"
                  >
                    <Check className="w-3 h-3" />
                    <span>Mark all read</span>
                  </button>
                )}
              </div>
              <div className="max-h-72 overflow-y-auto divide-y divide-slate-50">
                {notifications.length === 0 ? (
                  <div className="p-4 text-center text-xs text-slate-400">No notifications yet</div>
                ) : (
                  notifications.slice(0, 5).map(n => (
                    <div key={n.id} className={`p-3 text-xs ${n.is_read ? 'opacity-70' : 'bg-blue-50/40 font-medium'}`}>
                      <p className="text-slate-800">{n.message}</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">
                        {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  ))
                )}
              </div>
              <div className="px-4 py-2 border-t border-slate-100 text-center">
                <Link
                  to="/notifications"
                  onClick={() => setShowNotifMenu(false)}
                  className="text-xs text-blue-600 font-semibold hover:underline"
                >
                  View all notifications
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* User profile & Logout */}
        {user && (
          <div className="flex items-center space-x-3 pl-3 border-l border-slate-200">
            <div className="hidden md:block text-right">
              <p className="text-xs font-semibold text-slate-800">{user.name}</p>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                {user.role}
              </span>
            </div>
            <button
              onClick={handleLogout}
              title="Sign Out"
              className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
