from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PerformanceMetrics(BaseModel):
    resource_utilization_rate: float       # %
    conflict_resolution_rate: float        # %
    average_allocation_time_seconds: float # seconds
    policy_compliance_rate: float          # %
    fairness_index: float                  # %
    user_satisfaction_score: float         # score out of 5.0
    manual_intervention_rate: float        # %
    scheduling_accuracy: float             # %

class ResourceUtilizationItem(BaseModel):
    resource_id: int
    resource_name: str
    resource_type: str
    total_operating_hours: float
    allocated_hours: float
    utilization_percentage: float

class DepartmentFairnessItem(BaseModel):
    department_id: int
    department_name: str
    total_requests: int
    approved_requests: int
    rejected_requests: int
    satisfaction_rate: float
    allocated_hours: float

class BookingStatusBreakdown(BaseModel):
    status: str
    count: int

class AnalyticsOverviewResponse(BaseModel):
    total_bookings: int
    approved_bookings: int
    pending_bookings: int
    active_conflicts: int
    total_resources: int
    available_resources_now: int
    performance_metrics: PerformanceMetrics
    status_breakdown: List[BookingStatusBreakdown]
    resource_utilization: List[ResourceUtilizationItem]
    department_fairness: List[DepartmentFairnessItem]
