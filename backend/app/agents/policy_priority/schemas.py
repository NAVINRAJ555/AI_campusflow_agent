from pydantic import BaseModel, Field
from typing import List
from app.models.enums import PriorityLevel

class PolicyPriorityResult(BaseModel):
    policy_compliant: bool
    priority: PriorityLevel
    priority_score: float  # Numeric score for optimization (e.g., VERY_HIGH=100, HIGH=75, MEDIUM=50, LOW=25)
    policy_violations: List[str] = Field(default_factory=list)
    applied_rules: List[str] = Field(default_factory=list)
    reasoning: str
