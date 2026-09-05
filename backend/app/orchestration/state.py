from typing import TypedDict, List, Dict, Any, Optional

class BookingWorkflowState(TypedDict, total=False):
    booking_id: int
    raw_request_text: Optional[str]
    context: Dict[str, Any]
    structured_request: Dict[str, Any]
    resource_data: Dict[str, Any]
    policy_result: Dict[str, Any]
    priority: str
    conflicts: List[Dict[str, Any]]
    has_conflict: bool
    negotiation_options: List[Dict[str, Any]]
    optimization_result: Dict[str, Any]
    final_decision: Dict[str, Any]
    explanation: str
    decision_factors: Dict[str, Any]
    notifications: List[Dict[str, Any]]
    step_history: List[Dict[str, Any]]
    error: Optional[str]
