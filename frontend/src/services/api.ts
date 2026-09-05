import axios from 'axios';
import {
  User,
  Resource,
  ResourceAvailability,
  Booking,
  Policy,
  AgentTraceResponse,
  AnalyticsOverview,
  NotificationItem,
  AuditLogItem,
  CalendarEventItem
} from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('cf_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle unauthorized / expired tokens
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('cf_token');
      localStorage.removeItem('cf_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authApi = {
  login: (credentials: { email: string; password: string }) =>
    api.post('/auth/login', credentials),
  register: (userData: any) =>
    api.post('/auth/register', userData),
  getMe: () =>
    api.get<User>('/auth/me'),
};

// Users endpoints
export const usersApi = {
  getAll: () => api.get<User[]>('/users'),
  getById: (id: number) => api.get<User>(`/users/${id}`),
  update: (id: number, data: any) => api.put<User>(`/users/${id}`, data),
  delete: (id: number) => api.delete(`/users/${id}`),
  getDepartments: () => api.get<any[]>('/departments'),
};

// Resources endpoints
export const resourcesApi = {
  getAll: (type?: string, status?: string) =>
    api.get<Resource[]>('/resources', { params: { resource_type: type, status } }),
  getById: (id: number) =>
    api.get<Resource>(`/resources/${id}`),
  create: (data: any) =>
    api.post<Resource>('/resources', data),
  update: (id: number, data: any) =>
    api.put<Resource>(`/resources/${id}`, data),
  delete: (id: number) =>
    api.delete(`/resources/${id}`),
  getAvailability: (id: number, date?: string) =>
    api.get<ResourceAvailability>(`/resources/${id}/availability`, { params: { date } }),
  getAllAvailability: (date?: string) =>
    api.get<ResourceAvailability[]>('/resources/availability', { params: { date } }),
};

// Bookings endpoints
export const bookingsApi = {
  getAll: (status?: string, date?: string) =>
    api.get<Booking[]>('/bookings', { params: { status, date } }),
  getById: (id: number) =>
    api.get<Booking>(`/bookings/${id}`),
  create: (data: any, autoProcess: boolean = true) =>
    api.post<Booking>('/bookings', data, { params: { auto_process: autoProcess } }),
  cancel: (id: number) =>
    api.post<Booking>(`/bookings/${id}/cancel`),
  override: (id: number, data: { resource_id: number; date: string; start_time: string; end_time: string; reason: string }) =>
    api.post<Booking>(`/bookings/${id}/override`, data),
};

// AI NLP Understanding
export const aiApi = {
  understandRequest: (prompt: string) =>
    api.post<{ success: boolean; data: any; duration_ms: number; reasoning: string }>('/ai/understand-request', { prompt }),
};

// Scheduling & Agent Pipeline
export const schedulingApi = {
  processBooking: (id: number) =>
    api.post(`/scheduling/process/${id}`),
  getAgentTrace: (id: number) =>
    api.get<AgentTraceResponse>(`/agent-trace/${id}`),
};

// Negotiations
export const negotiationsApi = {
  getDetails: (bookingId: number) =>
    api.get(`/negotiations/${bookingId}`),
  selectOption: (bookingId: number, planId: string, adminReason?: string) =>
    api.post(`/negotiations/${bookingId}/select`, { plan_id: planId, admin_reason: adminReason }),
};

// Policies
export const policiesApi = {
  getAll: () => api.get<Policy[]>('/policies'),
  create: (data: any) => api.post<Policy>('/policies', data),
  update: (id: number, data: any) => api.put<Policy>(`/policies/${id}`, data),
  delete: (id: number) => api.delete(`/policies/${id}`),
};

// Calendar
export const calendarApi = {
  getEvents: (filters?: { resource_id?: number; resource_type?: string; department_id?: number; date?: string; status?: string }) =>
    api.get<CalendarEventItem[]>('/calendar', { params: filters }),
};

// Notifications
export const notificationsApi = {
  getAll: () => api.get<NotificationItem[]>('/notifications'),
  markRead: (id: number) => api.put(`/notifications/${id}/read`),
};

// Analytics
export const analyticsApi = {
  getOverview: () => api.get<AnalyticsOverview>('/analytics/overview'),
  getResourceUtilization: () => api.get('/analytics/resource-utilization'),
  getConflicts: () => api.get('/analytics/conflicts'),
  getFairness: () => api.get('/analytics/fairness'),
  getPolicyCompliance: () => api.get('/analytics/policy-compliance'),
};

// Audit Logs
export const auditLogsApi = {
  getAll: () => api.get<AuditLogItem[]>('/audit-logs'),
};

export default api;
