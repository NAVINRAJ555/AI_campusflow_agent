from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class StructuredDecisionFactors(BaseModel):
    decision: str  # APPROVED, REALLOCATED, RESCHEDULED, REJECTED
    priority_factor: str
    capacity_factor: str
    time_factor: str
    equipment_factor: str
    conflict_factor: str
    fairness_factor: str
    final_reason: str

class ExplanationResult(BaseModel):
    human_readable_explanation: str
    decision_factors: StructuredDecisionFactors
    notifications: List[Dict[str, Any]] = Field(default_factory=list)
    calendar_updates: List[Dict[str, Any]] = Field(default_factory=list)
