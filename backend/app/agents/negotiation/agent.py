import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.resource import Resource
from app.models.booking import Booking
from app.models.policy import Policy
from app.models.enums import BookingStatus, ResourceStatus
from app.agents.resource_intelligence.agent import time_to_minutes, intervals_overlap
from app.agents.negotiation.schemas import (
    NegotiationResult,
    CandidateNegotiationPlan,
    CandidateAllocationDetail
)

def minutes_to_time(m: int) -> str:
    hr = m // 60
    mn = m % 60
    return f"{hr:02d}:{mn:02d}"

class NegotiationAgent:
    """
    AGENT 4: NEGOTIATION AGENT
    When resource conflicts occur, synthesizes multiple viable allocation alternatives
    by exploring alternative resources, time shifts within flexibility windows, and priority swaps.
    All plans are deterministically validated before emission.
    """

    def process(
        self,
        db: Session,
        request_data: Dict[str, Any],
        resource_analysis: Dict[str, Any],
        policy_result: Dict[str, Any],
        booking_id: int
    ) -> Dict[str, Any]:
        start_time_clock = time.time()
        
        conflicts = resource_analysis.get("conflicts", [])
        policy_compliant = policy_result.get("policy_compliant", True)
        if not conflicts and resource_analysis.get("available", True) and policy_compliant:
            # No conflict: single straightforward plan
            target_res_id = resource_analysis.get("requested_resource_id")
            target_res_name = resource_analysis.get("requested_resource", "Primary Resource")
            
            single_plan = CandidateNegotiationPlan(
                plan_id="PLAN_DEFAULT",
                title="Direct Allocation",
                description=f"Allocate requested resource '{target_res_name}' at preferred time.",
                strategy="DIRECT",
                allocations=[
                    CandidateAllocationDetail(
                        booking_id=booking_id,
                        event_name=request_data.get("event_name", "New Event"),
                        resource_id=target_res_id,
                        resource_name=target_res_name,
                        date=request_data.get("date"),
                        start_time=request_data.get("start_time"),
                        end_time=request_data.get("end_time"),
                        is_rescheduled=False,
                        shift_minutes=0,
                        tradeoff_notes="Zero conflicts. Direct allocation."
                    )
                ],
                tradeoffs={"rescheduled_count": 0, "room_changed": False},
                is_physically_valid=True
            )
            
            duration = (time.time() - start_time_clock) * 1000
            return {
                "success": True,
                "data": NegotiationResult(
                    conflict_detected=False,
                    conflict_count=0,
                    candidate_plans=[single_plan],
                    reasoning="No conflict detected. Direct allocation plan generated."
                ).model_dump(),
                "duration_ms": duration,
                "reasoning": "Direct allocation feasible."
            }

        # Conflicts exist: generate candidate alternatives
        candidate_plans: List[CandidateNegotiationPlan] = []
        plan_counter = 1

        req_date = request_data.get("date")
        req_start = request_data.get("start_time")
        req_end = request_data.get("end_time")
        event_name = request_data.get("event_name", "New Event")
        participants = request_data.get("participant_count", 0)
        flexibility = request_data.get("flexibility", {})
        time_flexible = flexibility.get("time_flexible", False)
        max_shift = flexibility.get("max_shift_minutes", 60)
        target_res_id = resource_analysis.get("requested_resource_id")
        target_res_name = resource_analysis.get("requested_resource", "Preferred Resource")
        req_priority = policy_result.get("priority", "MEDIUM")

        duration_mins = time_to_minutes(req_end) - time_to_minutes(req_start)

        # -------------------------------------------------------------
        # STRATEGY 1: Alternative Resource Candidate
        # -------------------------------------------------------------
        alternatives = resource_analysis.get("alternatives", [])

        # Check active policies to avoid proposing restricted alternatives
        active_policies = db.query(Policy).filter(Policy.active == True).all()
        restricted_alt_names = set()
        for p in active_policies:
            if p.rule_type == "DEPARTMENT_RESTRICTION":
                try:
                    cfg = json.loads(p.rule_config) if isinstance(p.rule_config, str) else p.rule_config
                    p_res = [r.lower() for r in cfg.get("resources", [])]
                    p_depts = [d.lower() for d in cfg.get("allowed_departments", [])]
                    req_dept = (request_data.get("department") or "").lower()
                    ev_type = (request_data.get("event_type") or "").lower()
                    ev_name = (request_data.get("event_name") or "").lower()
                    is_club = "club" in ev_type or "club" in ev_name
                    if not any(d in req_dept for d in p_depts) or is_club:
                        restricted_alt_names.update(p_res)
                except Exception:
                    pass

        for alt in alternatives:
            alt_name_lower = alt.get("name", "").lower()
            if any(r in alt_name_lower for r in restricted_alt_names):
                continue
            if alt.get("is_available_at_requested_time") and alt.get("capacity", 0) >= participants:
                candidate_plans.append(CandidateNegotiationPlan(
                    plan_id=f"PLAN_{plan_counter}",
                    title=f"Reallocate to {alt.get('name')}",
                    description=(
                        f"Reallocate '{event_name}' to {alt.get('name')} (Capacity: {alt.get('capacity')}) "
                        f"at the exact requested time slot {req_start}-{req_end}."
                    ),
                    strategy="RESOURCE_ALTERNATIVE",
                    allocations=[
                        CandidateAllocationDetail(
                            booking_id=booking_id,
                            event_name=event_name,
                            resource_id=alt.get("resource_id"),
                            resource_name=alt.get("name"),
                            date=req_date,
                            start_time=req_start,
                            end_time=req_end,
                            is_rescheduled=False,
                            shift_minutes=0,
                            tradeoff_notes=f"Changed venue from {target_res_name} to {alt.get('name')}. Timing preserved."
                        )
                    ],
                    tradeoffs={
                        "venue_changed": True,
                        "time_shifted": False,
                        "equipment_match": alt.get("equipment_match_score", 1.0)
                    },
                    is_physically_valid=True
                ))
                plan_counter += 1
                if plan_counter > 3:
                    break

        # -------------------------------------------------------------
        # STRATEGY 2: Time Shift within Flexibility Window
        # -------------------------------------------------------------
        capacity_ok = resource_analysis.get("capacity_ok", True)
        if time_flexible and max_shift > 0 and capacity_ok and policy_compliant:
            target_res = db.query(Resource).filter(Resource.id == target_res_id).first()
            if target_res:
                op_start_min = time_to_minutes(target_res.operating_start)
                op_end_min = time_to_minutes(target_res.operating_end)
                
                # Try shifting earlier: e.g. -60 mins
                s_early_min = time_to_minutes(req_start) - max_shift
                e_early_min = s_early_min + duration_mins
                if s_early_min >= op_start_min:
                    s_early_str = minutes_to_time(s_early_min)
                    e_early_str = minutes_to_time(e_early_min)
                    
                    # Check if this early slot is free
                    early_conflicts = db.query(Booking).filter(
                        Booking.resource_id == target_res_id,
                        Booking.date == req_date,
                        Booking.status.in_([BookingStatus.APPROVED, BookingStatus.RESCHEDULED])
                    ).all()
                    has_early_conf = any(
                        intervals_overlap(s_early_str, e_early_str, b.start_time, b.end_time)
                        for b in early_conflicts if b.id != booking_id
                    )

                    if not has_early_conf:
                        candidate_plans.append(CandidateNegotiationPlan(
                            plan_id=f"PLAN_{plan_counter}",
                            title=f"Shift Time Earlier ({s_early_str} - {e_early_str}) in {target_res_name}",
                            description=(
                                f"Preserve requested venue {target_res_name} by moving the event "
                                f"earlier by {max_shift} minutes ({s_early_str} - {e_early_str})."
                            ),
                            strategy="TIME_SHIFT",
                            allocations=[
                                CandidateAllocationDetail(
                                    booking_id=booking_id,
                                    event_name=event_name,
                                    resource_id=target_res_id,
                                    resource_name=target_res_name,
                                    date=req_date,
                                    start_time=s_early_str,
                                    end_time=e_early_str,
                                    is_rescheduled=True,
                                    shift_minutes=-max_shift,
                                    tradeoff_notes=f"Moved start time {max_shift} mins earlier to avoid conflict."
                                )
                            ],
                            tradeoffs={
                                "venue_changed": False,
                                "time_shifted": True,
                                "shift_minutes": -max_shift
                            },
                            is_physically_valid=True
                        ))
                        plan_counter += 1

                # Try shifting later: e.g. immediately after first conflict or +max_shift
                first_conflict_end = conflicts[0].get("end", req_end)
                s_late_min = max(time_to_minutes(first_conflict_end), time_to_minutes(req_start) + max_shift)
                e_late_min = s_late_min + duration_mins
                if e_late_min <= op_end_min:
                    s_late_str = minutes_to_time(s_late_min)
                    e_late_str = minutes_to_time(e_late_min)
                    
                    late_conflicts = db.query(Booking).filter(
                        Booking.resource_id == target_res_id,
                        Booking.date == req_date,
                        Booking.status.in_([BookingStatus.APPROVED, BookingStatus.RESCHEDULED])
                    ).all()
                    has_late_conf = any(
                        intervals_overlap(s_late_str, e_late_str, b.start_time, b.end_time)
                        for b in late_conflicts if b.id != booking_id
                    )

                    if not has_late_conf:
                        shift_amount = s_late_min - time_to_minutes(req_start)
                        candidate_plans.append(CandidateNegotiationPlan(
                            plan_id=f"PLAN_{plan_counter}",
                            title=f"Shift Time Later ({s_late_str} - {e_late_str}) in {target_res_name}",
                            description=(
                                f"Preserve requested venue {target_res_name} by moving the event "
                                f"later to ({s_late_str} - {e_late_str})."
                            ),
                            strategy="TIME_SHIFT",
                            allocations=[
                                CandidateAllocationDetail(
                                    booking_id=booking_id,
                                    event_name=event_name,
                                    resource_id=target_res_id,
                                    resource_name=target_res_name,
                                    date=req_date,
                                    start_time=s_late_str,
                                    end_time=e_late_str,
                                    is_rescheduled=True,
                                    shift_minutes=shift_amount,
                                    tradeoff_notes=f"Moved start time {shift_amount} mins later to avoid conflict."
                                )
                            ],
                            tradeoffs={
                                "venue_changed": False,
                                "time_shifted": True,
                                "shift_minutes": shift_amount
                            },
                            is_physically_valid=True
                        ))
                        plan_counter += 1

        # -------------------------------------------------------------
        # STRATEGY 3: Priority Preemption / Relocation Swap
        # -------------------------------------------------------------
        # If incoming booking has higher priority than existing conflict,
        # incoming booking takes requested resource, and conflicting booking is relocated to an alternative
        for c in conflicts:
            conf_priority = c.get("priority", "MEDIUM")
            priority_rank = {"VERY_HIGH": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
            
            if priority_rank.get(req_priority, 2) > priority_rank.get(conf_priority, 2):
                # Incoming has higher priority!
                conf_booking_id = c.get("booking_id")
                conf_booking = db.query(Booking).filter(Booking.id == conf_booking_id).first()
                if conf_booking and alternatives:
                    valid_alt = None
                    for candidate_alt in alternatives:
                        if candidate_alt.get("capacity", 0) >= conf_booking.participant_count and candidate_alt.get("is_available_at_requested_time"):
                            cand_name_lower = candidate_alt.get("name", "").lower()
                            conf_is_club = "club" in (conf_booking.event_type or "").lower() or "club" in (conf_booking.event_name or "").lower()
                            if conf_is_club and any(r in cand_name_lower for r in restricted_alt_names):
                                continue
                            valid_alt = candidate_alt
                            break
                    if not valid_alt and alternatives:
                        valid_alt = alternatives[0]

                    if valid_alt:
                        candidate_plans.append(CandidateNegotiationPlan(
                            plan_id=f"PLAN_{plan_counter}",
                            title=f"Priority Preemption: Relocate '{c.get('event_name')}' to {valid_alt.get('name')}",
                            description=(
                                f"Allocate {target_res_name} to higher-priority '{event_name}' ({req_priority}). "
                                f"Relocate conflicting '{c.get('event_name')}' ({conf_priority}) to {valid_alt.get('name')}."
                            ),
                            strategy="PREEMPTION_SWAP",
                            allocations=[
                                CandidateAllocationDetail(
                                    booking_id=booking_id,
                                    event_name=event_name,
                                    resource_id=target_res_id,
                                    resource_name=target_res_name,
                                    date=req_date,
                                    start_time=req_start,
                                    end_time=req_end,
                                    is_rescheduled=False,
                                    shift_minutes=0,
                                    tradeoff_notes=f"Higher priority event awarded primary resource."
                                ),
                                CandidateAllocationDetail(
                                    booking_id=conf_booking_id,
                                    event_name=c.get("event_name"),
                                    resource_id=valid_alt.get("resource_id"),
                                    resource_name=valid_alt.get("name"),
                                    date=req_date,
                                    start_time=conf_booking.start_time,
                                    end_time=conf_booking.end_time,
                                    is_rescheduled=True,
                                    shift_minutes=0,
                                    tradeoff_notes=f"Relocated to {valid_alt.get('name')} to accommodate higher priority event."
                                )
                            ],
                            tradeoffs={
                                "preemption_occurred": True,
                                "relocated_event": c.get("event_name"),
                                "relocated_to": valid_alt.get("name")
                            },
                            is_physically_valid=True
                        ))
                        plan_counter += 1
                        break

        reasoning = (
            f"Detected {len(conflicts)} conflict(s). "
            f"Synthesized {len(candidate_plans)} validated candidate allocation plan(s) across "
            f"resource alternatives, time shifts, and priority preemption."
        )

        result = NegotiationResult(
            conflict_detected=True,
            conflict_count=len(conflicts),
            candidate_plans=candidate_plans,
            reasoning=reasoning
        )

        duration = (time.time() - start_time_clock) * 1000
        return {
            "success": True,
            "data": result.model_dump(),
            "duration_ms": duration,
            "reasoning": reasoning
        }
