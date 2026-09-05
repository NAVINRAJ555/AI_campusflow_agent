import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './layouts/DashboardLayout';

import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { CreateBooking } from './pages/CreateBooking';
import { MyBookings } from './pages/MyBookings';
import { BookingDetails } from './pages/BookingDetails';
import { ResourceAvailabilityPage } from './pages/ResourceAvailability';
import { ConflictResolution } from './pages/ConflictResolution';
import { CalendarView } from './pages/CalendarView';
import { NotificationsPage } from './pages/Notifications';
import { AnalyticsPage } from './pages/Analytics';
import { AdminResources } from './pages/AdminResources';
import { AdminPolicies } from './pages/AdminPolicies';
import { AdminUsers } from './pages/AdminUsers';
import { AgentTracePage } from './pages/AgentTrace';
import { AuditLogsPage } from './pages/AuditLogs';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="create-booking" element={<CreateBooking />} />
            <Route path="my-bookings" element={<MyBookings />} />
            <Route path="bookings/:id" element={<BookingDetails />} />
            <Route path="resources/availability" element={<ResourceAvailabilityPage />} />
            <Route path="negotiations/:bookingId" element={<ConflictResolution />} />
            <Route path="calendar" element={<CalendarView />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="admin/resources" element={<AdminResources />} />
            <Route path="admin/policies" element={<AdminPolicies />} />
            <Route path="admin/users" element={<AdminUsers />} />
            <Route path="admin/agent-trace" element={<AgentTracePage />} />
            <Route path="admin/audit-logs" element={<AuditLogsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};
