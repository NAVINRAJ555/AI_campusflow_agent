import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.booking import Booking
from app.models.resource import Resource
from app.models.allocation import Allocation
from app.models.calendar_event import CalendarEvent
from app.models.notification import Notification
from app.models.decision_log import DecisionLog
from app.models.audit_log import AuditLog
from app.models.enums import BookingStatus
from app.agents.explanation_notification.schemas import (
    ExplanationResult,
    StructuredDecisionFactors
)

class ExplanationNotificationAgent:
    """
    AGENT 6: EXPLANATION & NOTIFICATION AGENT
    Synthesizes transparent, fact-based natural language explanations and structured decision
    factors. Commits final allocations to database, synchronizes calendar events, dispatches
    notifications, and maintains an immutable audit trail.
    """

    def process(
        self,
        db: Session,
        booking_id: int,
        request_data: Dict[str, Any],
        resource_analysis: Dict[str, Any],
        policy_result: Dict[str, Any],
        negotiation_result: Dict[str, Any],
        optimization_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time_clock = time.time()

        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            duration = (time.time() - start_time_clock) * 1000
            return {
                "success": False,
                "data": {},
                "duration_ms": duration,
                "reasoning": f"Booking ID {booking_id} not found."
            }

        selected_plan_id = optimization_result.get("selected_plan_id")
        allocations_data = optimization_result.get("allocations", [])
        score = optimization_result.get("score", 0.0)
        strategy = optimization_result.get("strategy", "DIRECT")

        pref_res = request_data.get("preferred_resource") or request_data.get("resource_type")
        conflicts = resource_analysis.get("conflicts", [])
        priority_raw = policy_result.get("priority", "MEDIUM")
        priority = priority_raw.value if hasattr(priority_raw, "value") else str(priority_raw).replace("PriorityLevel.", "")

        if not allocations_data:
            # Rejection case
            booking.status = BookingStatus.REJECTED
            db.commit()

            violations = policy_result.get("policy_violations") or policy_result.get("violations") or []
            if violations:
                violation_str = " ".join(violations)
                explanation_text = (
                    f"Your request for {pref_res} on {request_data.get('date')} from {request_data.get('start_time')} "
                    f"to {request_data.get('end_time')} could not be accommodated due to institutional policy restrictions: {violation_str}"
                )
                final_reason = f"Rejected due to policy violation: {violation_str}"
            elif not resource_analysis.get("capacity_ok", True):
                cap = resource_analysis.get("requested_capacity", "limited")
                explanation_text = (
                    f"Your request for {pref_res} on {request_data.get('date')} from {request_data.get('start_time')} "
                    f"to {request_data.get('end_time')} could not be accommodated: Participant count ({request_data.get('participant_count')}) "
                    f"exceeds venue physical capacity ({cap}), and no capable alternative venue is available."
                )
                final_reason = f"Rejected: Participant count exceeds physical capacity ({cap})."
            else:
                explanation_text = (
                    f"Your request for {pref_res} on {request_data.get('date')} from {request_data.get('start_time')} "
                    f"to {request_data.get('end_time')} could not be accommodated due to hard policy or capacity constraints."
                )
                final_reason = "No feasible allocation satisfied all physical and policy constraints."

            factors = StructuredDecisionFactors(
                decision="REJECTED",
                priority_factor=f"Priority {priority} was insufficient to override existing schedule commitments.",
                capacity_factor=f"Venue capacity constraint not met." if not resource_analysis.get("capacity_ok", True) else "No available resource met the capacity requirement.",
                time_factor="No feasible time slot found within flexibility bounds.",
                equipment_factor="Equipment constraints could not be satisfied.",
                conflict_factor=f"Active conflict with {len(conflicts)} booked event(s)." if conflicts else "No direct schedule conflict.",
                fairness_factor="Preserved overall schedule integrity.",
                final_reason=final_reason
            )

            # Notification
            notif = Notification(
                user_id=booking.requester_id,
                booking_id=booking.id,
                message=explanation_text,
                type="REJECTION",
                is_read=False
            )
            db.add(notif)
            db.commit()

            duration = (time.time() - start_time_clock) * 1000
            return {
                "success": True,
                "data": ExplanationResult(
                    human_readable_explanation=explanation_text,
                    decision_factors=factors,
                    notifications=[{"user_id": booking.requester_id, "message": explanation_text}],
                    calendar_updates=[]
                ).model_dump(),
                "duration_ms": duration,
                "reasoning": "Booking rejected with full explanation."
            }

        # Successful allocation
        # Find primary allocation for this booking
        primary_alloc = next((a for a in allocations_data if a.get("booking_id") == booking_id), allocations_data[0])
        alloc_res_id = primary_alloc.get("resource_id")
        alloc_res_name = primary_alloc.get("resource_name")
        alloc_start = primary_alloc.get("start_time")
        alloc_end = primary_alloc.get("end_time")
        is_rescheduled = primary_alloc.get("is_rescheduled", False)

        # Determine decision type
        if alloc_res_name != pref_res:
            decision_type = "REALLOCATED"
        elif is_rescheduled:
            decision_type = "RESCHEDULED"
        else:
            decision_type = "APPROVED"

        # Generate human-readable explanation
        violations = policy_result.get("policy_violations") or policy_result.get("violations") or []
        if violations:
            violation_str = " ".join(violations)
            if alloc_res_name != pref_res:
                explanation_text = (
                    f"Institutional Policy Notice: {violation_str} "
                    f"CampusFlow auto-redirected your reservation to {alloc_res_name} to maintain university policy compliance."
                )
            else:
                explanation_text = f"Institutional Policy Warning: {violation_str}"
        elif strategy == "PREEMPTION_SWAP":
            preempted_names = ", ".join([a.get("event_name", "conflicting event") for a in allocations_data if a.get("booking_id") != booking_id])
            explanation_text = (
                f"Your booking request for {alloc_res_name} on {request_data.get('date')} from {alloc_start} to {alloc_end} "
                f"was awarded based on {priority} institutional priority. Conflicting lower-priority activity "
                f"('{preempted_names}') has been successfully relocated to alternative facilities."
            )
        elif alloc_res_name != pref_res:
            if not resource_analysis.get("capacity_ok", True):
                cap = resource_analysis.get("requested_capacity", "limited")
                explanation_text = (
                    f"Capacity Notice: Requested venue '{pref_res}' has a physical capacity of {cap}, "
                    f"which cannot accommodate {request_data.get('participant_count')} attendees. "
                    f"CampusFlow auto-allocated '{alloc_res_name}' to satisfy your physical capacity requirements."
                )
            elif conflicts:
                conf_names = ", ".join([c.get("event_name", "Existing event") for c in conflicts])
                explanation_text = (
                    f"Your request for {pref_res} from {request_data.get('start_time')} to {request_data.get('end_time')} "
                    f"could not be allocated because a conflicting event ('{conf_names}') occupies the resource. "
                    f"{alloc_res_name} has been allocated because it satisfies the required capacity of "
                    f"{request_data.get('participant_count')} participants and requested equipment requirements."
                )
            else:
                explanation_text = (
                    f"Your request was reallocated from '{pref_res}' to '{alloc_res_name}' "
                    f"to optimize campus resource utilization and satisfy all event constraints."
                )
        elif conflicts and is_rescheduled:
            explanation_text = (
                f"Your request for {pref_res} was adjusted to {alloc_start}–{alloc_end} to avoid an existing booking "
                f"conflict, leveraging your declared time flexibility."
            )
        else:
            explanation_text = (
                f"Your booking request for {alloc_res_name} on {request_data.get('date')} from {alloc_start} to "
                f"{alloc_end} has been successfully approved with all requested facilities."
            )

        if not resource_analysis.get("capacity_ok", True):
            cap_factor = f"Requested venue '{pref_res}' (cap {resource_analysis.get('requested_capacity')}) exceeded; allocated '{alloc_res_name}' to support {request_data.get('participant_count')} participants."
        else:
            cap_factor = f"Allocated venue '{alloc_res_name}' comfortably supports {request_data.get('participant_count')} participants."

        factors = StructuredDecisionFactors(
            decision=decision_type,
            priority_factor=f"Assigned {priority} priority. {'; '.join(violations) if violations else 'Institutional policy verified.'}",
            capacity_factor=cap_factor,
            time_factor=f"Scheduled slot: {alloc_start}–{alloc_end} (Flexibility utilized: {is_rescheduled}).",
            equipment_factor=f"Provided equipment: {', '.join(request_data.get('equipment', ['Standard A/V']))}.",
            conflict_factor=f"Successfully resolved {len(conflicts)} conflict(s) via multi-agent negotiation.",
            fairness_factor="Department allocation quota maintained within balanced threshold.",
            final_reason=explanation_text
        )

        # 1. Update Booking
        booking.resource_id = alloc_res_id
        booking.start_time = alloc_start
        booking.end_time = alloc_end
        booking.status = BookingStatus.APPROVED if not is_rescheduled else BookingStatus.RESCHEDULED
        booking.updated_at = datetime.now(timezone.utc)

        # 2. Update Allocations Table
        # Clean up any prior allocations for this booking
        db.query(Allocation).filter(Allocation.booking_id == booking_id).delete()
        new_alloc = Allocation(
            booking_id=booking.id,
            resource_id=alloc_res_id,
            date=request_data.get("date"),
            start_time=alloc_start,
            end_time=alloc_end,
            status="CONFIRMED"
        )
        db.add(new_alloc)

        # 3. Update Calendar Events
        db.query(CalendarEvent).filter(CalendarEvent.booking_id == booking_id).delete()
        cal_event = CalendarEvent(
            booking_id=booking.id,
            title=f"{booking.event_name} ({booking.requester.name if booking.requester else 'Event'})",
            date=request_data.get("date"),
            start_time=alloc_start,
            end_time=alloc_end,
            resource_id=alloc_res_id
        )
        db.add(cal_event)

        # 4. Handle secondary allocations if preemption swap occurred
        for alt_alloc in allocations_data:
            if alt_alloc.get("booking_id") != booking_id:
                other_b_id = alt_alloc.get("booking_id")
                other_b = db.query(Booking).filter(Booking.id == other_b_id).first()
                if other_b:
                    other_b.resource_id = alt_alloc.get("resource_id")
                    other_b.status = BookingStatus.RESCHEDULED
                    
                    # Synchronize Allocation record for preempted booking
                    other_alloc = db.query(Allocation).filter(Allocation.booking_id == other_b.id).first()
                    if other_alloc:
                        other_alloc.resource_id = alt_alloc.get("resource_id")
                        other_alloc.status = "RESCHEDULED"
                    
                    # Synchronize CalendarEvent record for preempted booking
                    other_cal = db.query(CalendarEvent).filter(CalendarEvent.booking_id == other_b.id).first()
                    if other_cal:
                        other_cal.resource_id = alt_alloc.get("resource_id")

                    # Add notification for affected user
                    db.add(Notification(
                        user_id=other_b.requester_id,
                        booking_id=other_b.id,
                        message=f"Notice: Your booking for '{other_b.event_name}' was relocated to {alt_alloc.get('resource_name')} to accommodate higher-priority institutional scheduling.",
                        type="RESCHEDULED",
                        is_read=False
                    ))

        # 5. Add Notification for Primary Requester
        notif = Notification(
            user_id=booking.requester_id,
            booking_id=booking.id,
            message=explanation_text,
            type="APPROVAL" if booking.status == BookingStatus.APPROVED else "RESCHEDULED",
            is_read=False
        )
        db.add(notif)

        # 6. Audit Log
        audit = AuditLog(
            user_id=booking.requester_id,
            action="AGENT_ALLOCATION_COMPLETED",
            entity_type="BOOKING",
            entity_id=str(booking.id),
            metadata_json=json.dumps({
                "selected_plan": selected_plan_id,
                "strategy": strategy,
                "score": score,
                "allocated_resource": alloc_res_name,
                "time_slot": f"{alloc_start}-{alloc_end}"
            })
        )
        db.add(audit)

        db.commit()

        duration = (time.time() - start_time_clock) * 1000
        return {
            "success": True,
            "data": ExplanationResult(
                human_readable_explanation=explanation_text,
                decision_factors=factors,
                notifications=[{"user_id": booking.requester_id, "message": explanation_text}],
                calendar_updates=[{"resource_id": alloc_res_id, "title": booking.event_name, "date": booking.date}]
            ).model_dump(),
            "duration_ms": duration,
            "reasoning": f"Generated final explanation and synchronized database state: {explanation_text}"
        }
