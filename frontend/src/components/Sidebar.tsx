import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  CalendarDays,
  PlusCircle,
  Building2,
  Calendar,
  Bell,
  BarChart3,
  Shield,
  FileText,
  Users,
  BrainCircuit,
  ClipboardList
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const isAdminOrManager = user?.role === 'SYSTEM_ADMIN' || user?.role === 'RESOURCE_MANAGER';
  const isSysAdmin = user?.role === 'SYSTEM_ADMIN';

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
      isActive
        ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
    }`;

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">Main Menu</p>
          <nav className="space-y-1">
            <NavLink to="/" end className={linkClass}>
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </NavLink>
            <NavLink to="/create-booking" className={linkClass}>
              <PlusCircle className="w-4 h-4" />
              <span>Create Booking</span>
            </NavLink>
            <NavLink to="/my-bookings" className={linkClass}>
              <CalendarDays className="w-4 h-4" />
              <span>My Bookings</span>
            </NavLink>
            <NavLink to="/resources/availability" className={linkClass}>
              <Building2 className="w-4 h-4" />
              <span>Resource Availability</span>
            </NavLink>
            <NavLink to="/calendar" className={linkClass}>
              <Calendar className="w-4 h-4" />
              <span>Campus Calendar</span>
            </NavLink>
            <NavLink to="/notifications" className={linkClass}>
              <Bell className="w-4 h-4" />
              <span>Notifications</span>
            </NavLink>
            <NavLink to="/analytics" className={linkClass}>
              <BarChart3 className="w-4 h-4" />
              <span>Analytics & Metrics</span>
            </NavLink>
          </nav>
        </div>

        {isAdminOrManager && (
          <div>
            <p className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">Administration</p>
            <nav className="space-y-1">
              <NavLink to="/admin/resources" className={linkClass}>
                <Building2 className="w-4 h-4" />
                <span>Resource Admin</span>
              </NavLink>
              <NavLink to="/admin/policies" className={linkClass}>
                <Shield className="w-4 h-4" />
                <span>Policy Engine</span>
              </NavLink>
              {isSysAdmin && (
                <NavLink to="/admin/users" className={linkClass}>
                  <Users className="w-4 h-4" />
                  <span>User Management</span>
                </NavLink>
              )}
              <NavLink to="/admin/agent-trace" className={linkClass}>
                <BrainCircuit className="w-4 h-4" />
                <span>Agent Decision Trace</span>
              </NavLink>
              <NavLink to="/admin/audit-logs" className={linkClass}>
                <ClipboardList className="w-4 h-4" />
                <span>Audit Trail</span>
              </NavLink>
            </nav>
          </div>
        )}
      </div>

      <div className="pt-4 border-t border-slate-100 text-[11px] text-slate-400 text-center">
        CampusFlow Multi-Agent System
        <br />
        Deterministic OR-Tools v9.15
      </div>
    </aside>
  );
};
