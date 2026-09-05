export type UserRole = 'STUDENT' | 'FACULTY' | 'DEPARTMENT_ADMIN' | 'RESOURCE_MANAGER' | 'SYSTEM_ADMIN';

export type PriorityLevel = 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW';

export type BookingStatus =
  | 'DRAFT'
  | 'PENDING'
  | 'PROCESSING'
  | 'CONFLICT'
  | 'NEGOTIATING'
  | 'APPROVED'
  | 'REJECTED'
  | 'RESCHEDULED'
  | 'CANCELLED'
  | 'COMPLETED';

export type ResourceStatus = 'ACTIVE' | 'MAINTENANCE' | 'INACTIVE';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  department_id?: number | null;
  department_name?: string | null;
  created_at: string;
}

export interface Department {
  id: number;
  name: string;
  code: string;
}

export interface Resource {
  id: number;
  name: string;
  resource_type: string;
  location: string;
  capacity: number;
  operating_start: string;
  operating_end: string;
  status: ResourceStatus;
  equipment: string[];
  maintenance_start?: string | null;
  maintenance_end?: string | null;
  created_at: string;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
  booking_id?: number | null;
  event_name?: string | null;
}

export interface ResourceAvailability {
  resource_id: number;
  resource_name: string;
  date: string;
  operating_start: string;
  operating_end: string;
  status: ResourceStatus;
  is_operational: boolean;
  maintenance_reason?: string | null;
  booked_slots: TimeSlot[];
  available_slots: TimeSlot[];
}

export interface SchedulingFlexibility {
  time_flexible: boolean;
  max_shift_minutes: number;
  alternative_dates?: string[];
}

export interface Booking {
  id: number;
  requester_id: number;
  requester_name?: string | null;
  requester_email?: string | null;
  department_name?: string | null;
  resource_id?: number | null;
  resource_name?: string | null;
  event_name: string;
  event_type: string;
  resource_type: string;
  date: string;
  start_time: string;
  end_time: string;
  participant_count: number;
  status: BookingStatus;
  priority: PriorityLevel;
  time_flexible: boolean;
  max_shift_minutes: number;
  equipment_needed: string[];
  raw_request?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Policy {
  id: number;
  name: string;
  description: string;
  rule_type: string;
  rule_config: string;
  priority: PriorityLevel;
  active: boolean;
}

export interface CandidateAllocation {
  booking_id: number;
  event_name: string;
  resource_id: number;
  resource_name: string;
  date: string;
  start_time: string;
  end_time: string;
  is_rescheduled: boolean;
  shift_minutes: number;
  tradeoff_notes?: string;
}

export interface CandidatePlan {
  plan_id: string;
  title: string;
  description: string;
  strategy: string;
  allocations: CandidateAllocation[];
  tradeoffs: Record<string, any>;
  score?: number;
  score_breakdown?: Record<string, number>;
  is_physically_valid?: boolean;
}

export interface StructuredDecisionFactors {
  decision: string;
  priority_factor: string;
  capacity_factor: string;
  time_factor: string;
  equipment_factor: string;
  conflict_factor: string;
  fairness_factor: string;
  final_reason: string;
}

export interface AgentTraceStep {
  agent_name: string;
  stage: string;
  status: string;
  summary: string;
  execution_time_ms: number;
  input_snapshot: Record<string, any>;
  output_snapshot: Record<string, any>;
  decision_factors?: Record<string, any>;
  timestamp: string;
}

export interface AgentTraceResponse {
  booking_id: number;
  event_name: string;
  current_status: string;
  total_execution_time_ms: number;
  steps: AgentTraceStep[];
  final_explanation?: string | null;
}

export interface PerformanceMetrics {
  resource_utilization_rate: number;
  conflict_resolution_rate: number;
  average_allocation_time_seconds: number;
  policy_compliance_rate: number;
  fairness_index: number;
  user_satisfaction_score: number;
  manual_intervention_rate: number;
  scheduling_accuracy: number;
}

export interface ResourceUtilizationItem {
  resource_id: number;
  resource_name: string;
  resource_type: string;
  total_operating_hours: number;
  allocated_hours: number;
  utilization_percentage: number;
}

export interface DepartmentFairnessItem {
  department_id: number;
  department_name: string;
  total_requests: number;
  approved_requests: number;
  rejected_requests: number;
  satisfaction_rate: number;
  allocated_hours: number;
}

export interface BookingStatusBreakdown {
  status: string;
  count: number;
}

export interface AnalyticsOverview {
  total_bookings: number;
  approved_bookings: number;
  pending_bookings: number;
  active_conflicts: number;
  total_resources: number;
  available_resources_now: number;
  performance_metrics: PerformanceMetrics;
  status_breakdown: BookingStatusBreakdown[];
  resource_utilization: ResourceUtilizationItem[];
  department_fairness: DepartmentFairnessItem[];
}

export interface NotificationItem {
  id: number;
  user_id: number;
  booking_id?: number | null;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

export interface AuditLogItem {
  id: number;
  user_id?: number | null;
  user_name: string;
  action: string;
  entity_type: string;
  entity_id: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface CalendarEventItem {
  id: number;
  booking_id: number;
  title: string;
  event_name: string;
  resource_id: number;
  resource_name: string;
  resource_type: string;
  date: string;
  start_time: string;
  end_time: string;
  department_name: string;
  status: string;
  priority: string;
}
