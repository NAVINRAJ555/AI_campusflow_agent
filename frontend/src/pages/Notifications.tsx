import React, { useEffect, useState } from 'react';
import { notificationsApi } from '../services/api';
import { NotificationItem } from '../types';
import { Bell, Check, CheckCheck, Clock, ShieldCheck, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifs = async () => {
    setLoading(true);
    try {
      const res = await notificationsApi.getAll();
      setNotifications(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifs();
  }, []);

  const handleMarkRead = async (id: number) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    for (const n of notifications.filter(n => !n.is_read)) {
      await notificationsApi.markRead(n.id);
    }
    setNotifications(notifications.map(n => ({ ...n, is_read: true })));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Notifications & Alerts</h1>
          <p className="text-xs text-slate-500 mt-1">Autonomous multi-agent notifications regarding your resource allocations.</p>
        </div>
        {notifications.some(n => !n.is_read) && (
          <button
            onClick={handleMarkAllRead}
            className="px-3.5 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold text-xs rounded-lg flex items-center space-x-1.5 transition-colors"
          >
            <CheckCheck className="w-4 h-4" />
            <span>Mark All as Read</span>
          </button>
        )}
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm divide-y divide-slate-100 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading notifications...</div>
        ) : notifications.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">No notifications to display.</div>
        ) : (
          notifications.map(n => (
            <div
              key={n.id}
              className={`p-4 flex items-start justify-between gap-4 transition-colors ${
                n.is_read ? 'bg-white' : 'bg-blue-50/40'
              }`}
            >
              <div className="flex items-start space-x-3.5">
                <div className={`p-2 rounded-xl mt-0.5 shrink-0 ${
                  n.type === 'APPROVAL'
                    ? 'bg-emerald-100 text-emerald-700'
                    : n.type === 'RESCHEDULED'
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-blue-100 text-blue-700'
                }`}>
                  <Bell className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs text-slate-800 leading-relaxed font-medium">{n.message}</p>
                  <div className="flex items-center space-x-3 mt-1.5 text-[11px] text-slate-400">
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(n.created_at).toLocaleString()}</span>
                    </span>
                    {n.booking_id && (
                      <Link
                        to={`/bookings/${n.booking_id}`}
                        className="font-semibold text-blue-600 hover:underline"
                      >
                        View Booking Details →
                      </Link>
                    )}
                  </div>
                </div>
              </div>

              {!n.is_read && (
                <button
                  onClick={() => handleMarkRead(n.id)}
                  title="Mark as read"
                  className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-colors shrink-0"
                >
                  <Check className="w-4 h-4" />
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
