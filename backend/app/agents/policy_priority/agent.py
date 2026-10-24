import json
import time
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.policy import Policy
from app.models.enums import PriorityLevel
from app.agents.policy_priority.schemas import PolicyPriorityResult

class PolicyPriorityAgent:
    """
    AGENT 3: POLICY & PRIORITY AGENT
    Reads active policies from the database to validate policy compliance, detect violations,
    and dynamically compute institutional priority (VERY_HIGH, HIGH, MEDIUM, LOW).
    """

    def process(
        self,
        db: Session,
        request_data: Dict[str, Any],
        resource_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time_clock = time.time()
        
        event_type = request_data.get("event_type", "department_seminar").lower()
        event_name = request_data.get("event_name", "").lower()
        dept_name = request_data.get("department", "").lower()
        booking_date = request_data.get("date", "")
        participant_count = request_data.get("participant_count", 0)

        # 1. Base priority derivation from event type & institutional importance
        priority = PriorityLevel.MEDIUM
        priority_score = 50.0
        reasoning_parts = []

        if "placement" in event_type or "placement" in event_name:
            priority = PriorityLevel.VERY_HIGH
            priority_score = 100.0
            reasoning_parts.append("Placement activities hold university-wide critical precedence.")
        elif "exam" in event_type or "examination" in event_name:
            priority = PriorityLevel.VERY_HIGH
            priority_score = 100.0
            reasoning_parts.append("Official examinations take non-preemptible priority.")
        elif "technical_event" in event_type or "symposium" in event_name or "hackathon" in event_name:
            priority = PriorityLevel.HIGH
            priority_score = 75.0
            reasoning_parts.append("University-level academic and technical symposiums receive high priority.")
        elif "club" in event_type or "club" in event_name:
            priority = PriorityLevel.LOW
            priority_score = 25.0
            reasoning_parts.append("Student club activities operate on standard baseline priority.")
        else:
            priority = PriorityLevel.MEDIUM
            priority_score = 50.0
            reasoning_parts.append("Standard departmental academic event receives medium priority.")

        # 2. Database Policy Evaluation
        active_policies = db.query(Policy).filter(Policy.active == True).all()
        violations: List[str] = []
        applied_rules: List[str] = []

        for policy in active_policies:
            try:
                config = json.loads(policy.rule_config) if isinstance(policy.rule_config, str) else policy.rule_config
            except Exception:
                config = {}

            rule_type = policy.rule_type.upper()

            # Rule: Capacity Check
            if rule_type == "CAPACITY_CHECK":
                if not resource_analysis.get("capacity_ok", True):
                    cap = resource_analysis.get("requested_capacity", "limited")
                    violations.append(
                        f"Policy '{policy.name}': Participant count ({request_data.get('participant_count')}) exceeds resource physical capacity ({cap})."
                    )
                applied_rules.append(policy.name)

            # Rule: Operating Hours
            elif rule_type == "OPERATING_HOURS":
                if not resource_analysis.get("operating_hours_ok", True):
                    violations.append(f"Policy '{policy.name}': Booking falls outside resource official operating hours.")
                applied_rules.append(policy.name)

            # Rule: Department Restriction (e.g. specialized labs)
            elif rule_type == "DEPARTMENT_RESTRICTION":
                allowed_depts = [d.lower() for d in config.get("allowed_departments", [])]
                restricted_resources = [r.lower() for r in config.get("resources", [])]
                req_res = resource_analysis.get("requested_resource", "").lower()

                if any(r in req_res for r in restricted_resources) and allowed_depts:
                    is_club = "club" in event_type or "club" in event_name
                    if not any(d in dept_name for d in allowed_depts) or is_club:
                        violations.append(
                            f"Policy '{policy.name}': Resource '{req_res}' is restricted to CSE/IT academic coursework. Student club and unauthorized activities are prohibited."
                        )
                applied_rules.append(policy.name)

            # Rule: Priority Elevation
            elif rule_type == "PRIORITY_ELEVATION":
                target_events = [e.lower() for e in config.get("event_types", [])]
                if any(e in event_type for e in target_events) or any(e in event_name for e in target_events):
                    elevated_priority = getattr(PriorityLevel, config.get("elevate_to", "HIGH"), PriorityLevel.HIGH)
                    if elevated_priority == PriorityLevel.VERY_HIGH and priority != PriorityLevel.VERY_HIGH:
                        priority = PriorityLevel.VERY_HIGH
                        priority_score = 100.0
                        reasoning_parts.append(f"Elevated by policy '{policy.name}' to VERY_HIGH.")
                    elif elevated_priority == PriorityLevel.HIGH and priority in [PriorityLevel.LOW, PriorityLevel.MEDIUM]:
                        priority = PriorityLevel.HIGH
                        priority_score = 75.0
                        reasoning_parts.append(f"Elevated by policy '{policy.name}' to HIGH.")
                    applied_rules.append(policy.name)

            # Rule: Advance Notice
            elif rule_type == "ADVANCE_BOOKING":
                min_days = config.get("min_days_notice", 0)
                try:
                    target_dt = datetime.strptime(booking_date, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    diff_days = (target_dt - today).days
                    if diff_days < min_days:
                        violations.append(f"Policy '{policy.name}': Requires minimum {min_days} days advance notice.")
                    applied_rules.append(policy.name)
                except Exception:
                    pass

        is_compliant = len(violations) == 0
        final_reasoning = f"{' '.join(reasoning_parts)} Checked {len(applied_rules)} policies with {len(violations)} violations."

        result = PolicyPriorityResult(
            policy_compliant=is_compliant,
            priority=priority,
            priority_score=priority_score,
            policy_violations=violations,
            applied_rules=applied_rules,
            reasoning=final_reasoning
        )

        duration = (time.time() - start_time_clock) * 1000
        return {
            "success": True,
            "data": result.model_dump(),
            "duration_ms": duration,
            "reasoning": final_reasoning
        }
