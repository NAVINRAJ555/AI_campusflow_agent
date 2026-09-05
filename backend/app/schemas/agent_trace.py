from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class AgentTraceStep(BaseModel):
    agent_name: str
    stage: str
    status: str  # SUCCESS, CONFLICT_DETECTED, SKIPPED, FAILED
    summary: str
    execution_time_ms: float
    input_snapshot: Dict[str, Any]
    output_snapshot: Dict[str, Any]
    decision_factors: Dict[str, Any] = {}
    timestamp: datetime

class AgentTraceResponse(BaseModel):
    booking_id: int
    event_name: str
    current_status: str
    total_execution_time_ms: float
    steps: List[AgentTraceStep]
    final_explanation: Optional[str] = None
