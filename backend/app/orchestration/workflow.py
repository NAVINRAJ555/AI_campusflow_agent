import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

from app.models.booking import Booking
from app.models.decision_log import DecisionLog
from app.orchestration.state import BookingWorkflowState
from app.agents.request_understanding import RequestUnderstandingAgent
from app.agents.resource_intelligence import ResourceIntelligenceAgent
from app.agents.policy_priority import PolicyPriorityAgent
from app.agents.negotiation import NegotiationAgent
from app.agents.optimization import OptimizationAgent
from app.agents.explanation_notification import ExplanationNotificationAgent

logger = logging.getLogger(__name__)

class CampusFlowOrchestrator:
    """
    Stateful multi-agent orchestrator using LangGraph.
    Executes: Understand -> Resource Intelligence -> Policy/Priority -> Conflict? -> [Negotiate -> Optimize | Optimize] -> Explain.
    Maintains full decision transparency in the database.
    """

    def __init__(self, db: Session):
        self.db = db
        self.understanding_agent = RequestUnderstandingAgent()
        self.intelligence_agent = ResourceIntelligenceAgent()
        self.policy_agent = PolicyPriorityAgent()
        self.negotiation_agent = NegotiationAgent()
        self.optimization_agent = OptimizationAgent()
        self.explanation_agent = ExplanationNotificationAgent()
        self.graph = self._build_graph()

    def _log_decision(self, booking_id: int, agent_name: str, input_data: Any, output_data: Any, reasoning: str):
        """Persists agent step snapshot into database decision_logs."""
        try:
            log_entry = DecisionLog(
                booking_id=booking_id,
                agent_name=agent_name,
                input_data=json.dumps(input_data, default=str),
                output_data=json.dumps(output_data, default=str),
                reasoning=reasoning,
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log decision step for {agent_name}: {e}")
            self.db.rollback()

    def _node_understand(self, state: BookingWorkflowState) -> Dict[str, Any]:
        raw_text = state.get("raw_request_text")
        context = state.get("context", {})
        booking_id = state.get("booking_id")
        
        # If we already have structured request from direct form, use it
        structured = state.get("structured_request")
        if not structured and raw_text:
            res = self.understanding_agent.process(raw_text, context)
            structured = res["data"]
            self._log_decision(
                booking_id=booking_id,
                agent_name="Request Understanding Agent",
                input_data={"raw_text": raw_text, "context": context},
                output_data=structured,
                reasoning=res["reasoning"]
            )
        elif not structured:
            # Fallback to database booking row
            booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
            if booking:
                structured = {
                    "resource_type": booking.resource_type,
                    "preferred_resource": booking.resource.name if booking.resource else None,
                    "event_name": booking.event_name,
                    "event_type": booking.event_type,
                    "department": booking.requester.department.name if (booking.requester and booking.requester.department) else "General",
                    "date": booking.date,
                    "start_time": booking.start_time,
                    "end_time": booking.end_time,
                    "participant_count": booking.participant_count,
                    "equipment": [eq.equipment_name for eq in booking.equipment_needed],
                    "flexibility": {
                        "time_flexible": booking.time_flexible,
                        "max_shift_minutes": booking.max_shift_minutes
                    }
                }

        step = {
            "agent": "Request Understanding Agent",
            "summary": f"Parsed parameters for event '{structured.get('event_name')}'",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history = state.get("step_history", []) + [step]

        return {
            "structured_request": structured,
            "step_history": history
        }

    def _node_resource_intelligence(self, state: BookingWorkflowState) -> Dict[str, Any]:
        booking_id = state.get("booking_id")
        req_data = state["structured_request"]

        res = self.intelligence_agent.process(self.db, req_data, current_booking_id=booking_id)
        resource_data = res["data"]

        self._log_decision(
            booking_id=booking_id,
            agent_name="Resource Intelligence Agent",
            input_data=req_data,
            output_data=resource_data,
            reasoning=res["reasoning"]
        )

        conflicts = resource_data.get("conflicts", [])
        has_conflict = len(conflicts) > 0 or not resource_data.get("available", True)

        step = {
            "agent": "Resource Intelligence Agent",
            "summary": f"Availability: {resource_data.get('available')}, Conflicts detected: {len(conflicts)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history = state.get("step_history", []) + [step]

        return {
            "resource_data": resource_data,
            "conflicts": conflicts,
            "has_conflict": has_conflict,
            "step_history": history
        }

    def _node_policy_priority(self, state: BookingWorkflowState) -> Dict[str, Any]:
        booking_id = state.get("booking_id")
        req_data = state["structured_request"]
        res_data = state["resource_data"]

        res = self.policy_agent.process(self.db, req_data, res_data)
        policy_data = res["data"]

        self._log_decision(
            booking_id=booking_id,
            agent_name="Policy & Priority Agent",
            input_data={"request": req_data, "resource": res_data},
            output_data=policy_data,
            reasoning=res["reasoning"]
        )

        step = {
            "agent": "Policy & Priority Agent",
            "summary": f"Assigned Priority: {policy_data.get('priority')}, Compliant: {policy_data.get('policy_compliant')}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history = state.get("step_history", []) + [step]

        return {
            "policy_result": policy_data,
            "priority": str(policy_data.get("priority")),
            "step_history": history
        }

    def _check_conflict(self, state: BookingWorkflowState) -> str:
        """Conditional routing branch."""
        if state.get("has_conflict", False):
            return "negotiation"
        return "optimization"

    def _node_negotiation(self, state: BookingWorkflowState) -> Dict[str, Any]:
        booking_id = state.get("booking_id")
        req_data = state["structured_request"]
        res_data = state["resource_data"]
        pol_data = state["policy_result"]

        res = self.negotiation_agent.process(
            db=self.db,
            request_data=req_data,
            resource_analysis=res_data,
            policy_result=pol_data,
            booking_id=booking_id
        )
        neg_data = res["data"]
        candidate_plans = neg_data.get("candidate_plans", [])

        self._log_decision(
            booking_id=booking_id,
            agent_name="Negotiation Agent",
            input_data={"conflicts": state.get("conflicts"), "policy": pol_data},
            output_data=neg_data,
            reasoning=res["reasoning"]
        )

        step = {
            "agent": "Negotiation Agent",
            "summary": f"Generated {len(candidate_plans)} candidate alternative plans under conflict",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history = state.get("step_history", []) + [step]

        return {
            "negotiation_options": candidate_plans,
            "step_history": history
        }

    def _node_optimization(self, state: BookingWorkflowState) -> Dict[str, Any]:
        booking_id = state.get("booking_id")
        req_data = state["structured_request"]
        pol_data = state["policy_result"]
        plans = state.get("negotiation_options")

        # If no negotiation occurred (no conflict), generate single direct plan
        if not plans:
            res_data = state["resource_data"]
            plans = [{
                "plan_id": "PLAN_DIRECT",
                "title": "Direct Allocation",
                "strategy": "DIRECT",
                "description": "Standard direct allocation without conflicts.",
                "allocations": [{
                    "booking_id": booking_id,
                    "event_name": req_data.get("event_name"),
                    "resource_id": res_data.get("requested_resource_id"),
                    "resource_name": res_data.get("requested_resource"),
                    "date": req_data.get("date"),
                    "start_time": req_data.get("start_time"),
                    "end_time": req_data.get("end_time"),
                    "is_rescheduled": False,
                    "shift_minutes": 0
                }],
                "is_physically_valid": True,
                "tradeoffs": {}
            }]

        res = self.optimization_agent.process(
            candidate_plans=plans,
            request_data=req_data,
            policy_data=pol_data
        )
        opt_data = res["data"]

        self._log_decision(
            booking_id=booking_id,
            agent_name="Optimization Agent",
            input_data={"candidate_plans_count": len(plans)},
            output_data=opt_data,
            reasoning=res["reasoning"]
        )

        step = {
            "agent": "Optimization Agent",
            "summary": f"Google OR-Tools selected {opt_data.get('selected_plan_id')} with score {opt_data.get('score')}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history = state.get("step_history", []) + [step]

        return {
            "optimization_result": opt_data,
            "step_history": history
        }

    def _node_explanation_notification(self, state: BookingWorkflowState) -> Dict[str, Any]:
        booking_id = state.get("booking_id")
        req_data = state["structured_request"]
        res_data = state["resource_data"]
        pol_data = state["policy_result"]
        neg_data = {"candidate_plans": state.get("negotiation_options", [])}
        opt_data = state["optimization_result"]

        res = self.explanation_agent.process(
            db=self.db,
            booking_id=booking_id,
            request_data=req_data,
            resource_analysis=res_data,
            policy_result=pol_data,
            negotiation_result=neg_data,
            optimization_result=opt_data
        )
        exp_data = res["data"]

        self._log_decision(
            booking_id=booking_id,
            agent_name="Explanation & Notification Agent",
            input_data={"optimization": opt_data},
            output_data=exp_data,
            reasoning=res["reasoning"]
        )

        step = {
            "agent": "Explanation & Notification Agent",
            "summary": "Generated transparent decision factors and updated database/calendar/notifications.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history = state.get("step_history", []) + [step]

        return {
            "explanation": exp_data.get("human_readable_explanation"),
            "decision_factors": exp_data.get("decision_factors"),
            "notifications": exp_data.get("notifications", []),
            "final_decision": exp_data,
            "step_history": history
        }

    def _build_graph(self):
        builder = StateGraph(BookingWorkflowState)

        # Register nodes
        builder.add_node("request_understanding", self._node_understand)
        builder.add_node("resource_intelligence", self._node_resource_intelligence)
        builder.add_node("policy_priority", self._node_policy_priority)
        builder.add_node("negotiation", self._node_negotiation)
        builder.add_node("optimization", self._node_optimization)
        builder.add_node("explanation_notification", self._node_explanation_notification)

        # Edges
        builder.add_edge(START, "request_understanding")
        builder.add_edge("request_understanding", "resource_intelligence")
        builder.add_edge("resource_intelligence", "policy_priority")

        # Conditional branch
        builder.add_conditional_edges(
            "policy_priority",
            self._check_conflict,
            {
                "negotiation": "negotiation",
                "optimization": "optimization"
            }
        )

        builder.add_edge("negotiation", "optimization")
        builder.add_edge("optimization", "explanation_notification")
        builder.add_edge("explanation_notification", END)

        return builder.compile()

    def run(self, booking_id: int, raw_text: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> BookingWorkflowState:
        """Executes the complete compiled multi-agent graph."""
        initial_state: BookingWorkflowState = {
            "booking_id": booking_id,
            "raw_request_text": raw_text,
            "context": context or {},
            "step_history": []
        }
        final_state = self.graph.invoke(initial_state)
        return final_state
