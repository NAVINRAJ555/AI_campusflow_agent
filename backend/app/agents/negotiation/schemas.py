from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CandidateAllocationDetail(BaseModel):
    booking_id: int
    event_name: str
    resource_id: int
    resource_name: str
    date: str
    start_time: str
    end_time: str
    is_rescheduled: bool = False
    shift_minutes: int = 0
    tradeoff_notes: str = ""

class CandidateNegotiationPlan(BaseModel):
    plan_id: str
    title: str
    description: str
    strategy: str  # RESOURCE_ALTERNATIVE, TIME_SHIFT, PREEMPTION_SWAP, SPLIT
    allocations: List[CandidateAllocationDetail]
    tradeoffs: Dict[str, Any] = {}
    is_physically_valid: bool = True

class NegotiationResult(BaseModel):
    conflict_detected: bool
    conflict_count: int
    candidate_plans: List[CandidateNegotiationPlan] = Field(default_factory=list)
    reasoning: str
