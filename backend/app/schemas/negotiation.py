from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.enums import ConflictType

class CandidateAllocation(BaseModel):
    booking_id: int
    resource_id: int
    resource_name: str
    date: str
    start_time: str
    end_time: str
    is_rescheduled: bool = False
    shift_minutes: int = 0

class CandidatePlan(BaseModel):
    plan_id: str
    description: str
    score: float = 0.0
    allocations: List[CandidateAllocation]
    tradeoffs: Dict[str, Any] = {}

class NegotiationOptionResponse(BaseModel):
    id: int
    negotiation_case_id: int
    option_data: Dict[str, Any]
    score: float
    selected: bool

    class Config:
        from_attributes = True

class NegotiationCaseResponse(BaseModel):
    id: int
    booking_id: int
    status: str
    conflict_type: ConflictType
    created_at: datetime
    resolved_at: Optional[datetime] = None
    options: List[NegotiationOptionResponse] = []

    class Config:
        from_attributes = True

class NegotiationSelectionRequest(BaseModel):
    plan_id: str
    admin_reason: Optional[str] = None
