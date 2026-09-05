import logging
import time
from typing import Optional, Dict, Any
from app.llm.factory import get_llm_provider
from app.agents.request_understanding.schemas import StructuredBookingRequest

logger = logging.getLogger(__name__)

class RequestUnderstandingAgent:
    """
    AGENT 1: REQUEST UNDERSTANDING AGENT
    Converts unstructured natural-language booking requests into strictly validated
    structured booking models using LLM with deterministic regex/heuristic fallback.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()
        system_prompt = (
            "You are the Request Understanding Agent in CampusFlow university system. "
            "Extract all booking fields into structured format: resource_type, preferred_resource, "
            "event_name, event_type, date, start_time, end_time, participant_count, equipment, "
            "and flexibility. Output MUST match the StructuredBookingRequest schema exactly."
        )

        try:
            structured = self.llm.generate_structured(text, StructuredBookingRequest, system_prompt)
            duration = (time.time() - start_time) * 1000
            
            # Enrich with context if missing
            if context and not structured.department and context.get("department_name"):
                structured.department = context["department_name"]

            return {
                "success": True,
                "data": structured.model_dump(),
                "duration_ms": duration,
                "reasoning": f"Successfully parsed and validated booking request for '{structured.event_name}' on {structured.date}."
            }
        except Exception as e:
            logger.error(f"Error in RequestUnderstandingAgent: {e}")
            duration = (time.time() - start_time) * 1000
            # Fallback extraction
            fallback_res = self.llm.fallback.generate_structured(text, StructuredBookingRequest) if hasattr(self.llm, "fallback") else None
            return {
                "success": bool(fallback_res),
                "data": fallback_res.model_dump() if fallback_res else {},
                "duration_ms": duration,
                "reasoning": f"Extracted via deterministic fallback parser: {e}"
            }
