from pydantic import BaseModel, Field
from typing import List, Optional

class BookingConflictDetail(BaseModel):
    booking_id: int
    event_name: str
    requester_name: Optional[str] = None
    priority: str
    start: str
    end: str
    overlap_minutes: int
    reason: str = "Time overlap with existing confirmed booking"

class AlternativeResourceCandidate(BaseModel):
    resource_id: int
    name: str
    resource_type: str
    capacity: int
    location: str
    equipment_available: List[str]
    equipment_match_score: float  # 0.0 - 1.0
    capacity_ratio: float         # participant_count / capacity
    is_available_at_requested_time: bool

class ResourceAnalysisResult(BaseModel):
    requested_resource: str
    requested_resource_id: Optional[int] = None
    available: bool
    capacity_ok: bool
    operating_hours_ok: bool
    maintenance_ok: bool
    equipment_ok: bool
    conflicts: List[BookingConflictDetail] = Field(default_factory=list)
    alternatives: List[AlternativeResourceCandidate] = Field(default_factory=list)
    reasoning: str
