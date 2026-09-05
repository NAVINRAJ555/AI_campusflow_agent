import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.resource import Resource
from app.models.booking import Booking
from app.models.enums import BookingStatus, ResourceStatus
from app.agents.resource_intelligence.schemas import (
    ResourceAnalysisResult,
    BookingConflictDetail,
    AlternativeResourceCandidate
)

def time_to_minutes(t_str: str) -> int:
    parts = t_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def intervals_overlap(s1: str, e1: str, s2: str, e2: str) -> bool:
    start1 = time_to_minutes(s1)
    end1 = time_to_minutes(e1)
    start2 = time_to_minutes(s2)
    end2 = time_to_minutes(e2)
    return max(start1, start2) < min(end1, end2)

def calculate_overlap_minutes(s1: str, e1: str, s2: str, e2: str) -> int:
    start1 = time_to_minutes(s1)
    end1 = time_to_minutes(e1)
    start2 = time_to_minutes(s2)
    end2 = time_to_minutes(e2)
    overlap = min(end1, end2) - max(start1, start2)
    return max(0, overlap)

class ResourceIntelligenceAgent:
    """
    AGENT 2: RESOURCE INTELLIGENCE AGENT
    Queries database state to analyze availability, capacity, equipment, operating hours,
    maintenance windows, and existing booking conflicts. Computes alternative resources.
    """

    def process(self, db: Session, request_data: Dict[str, Any], current_booking_id: Optional[int] = None) -> Dict[str, Any]:
        start_time_clock = time.time()
        
        pref_name = request_data.get("preferred_resource")
        res_type = request_data.get("resource_type", "seminar_hall")
        date_str = request_data.get("date")
        req_start = request_data.get("start_time")
        req_end = request_data.get("end_time")
        participants = request_data.get("participant_count", 0)
        req_equipment = request_data.get("equipment", [])

        # Find target resource
        target_resource: Optional[Resource] = None
        if pref_name:
            target_resource = db.query(Resource).filter(Resource.name.ilike(f"%{pref_name}%")).first()
        
        if not target_resource:
            target_resource = db.query(Resource).filter(
                Resource.resource_type == res_type,
                Resource.status == ResourceStatus.ACTIVE
            ).first()

        if not target_resource:
            duration = (time.time() - start_time_clock) * 1000
            return {
                "success": False,
                "data": ResourceAnalysisResult(
                    requested_resource=pref_name or res_type,
                    available=False,
                    capacity_ok=False,
                    operating_hours_ok=False,
                    maintenance_ok=False,
                    equipment_ok=False,
                    conflicts=[],
                    alternatives=[],
                    reasoning=f"No resource matching '{pref_name or res_type}' found in database."
                ).model_dump(),
                "duration_ms": duration,
                "reasoning": "Resource not found."
            }

        # 1. Capacity check
        capacity_ok = target_resource.capacity >= participants

        # 2. Operating hours check
        req_s_min = time_to_minutes(req_start)
        req_e_min = time_to_minutes(req_end)
        op_s_min = time_to_minutes(target_resource.operating_start)
        op_e_min = time_to_minutes(target_resource.operating_end)
        operating_hours_ok = (req_s_min >= op_s_min) and (req_e_min <= op_e_min)

        # 3. Maintenance check
        maintenance_ok = (target_resource.status == ResourceStatus.ACTIVE)
        if target_resource.maintenance_start and target_resource.maintenance_end:
            try:
                booking_dt = datetime.strptime(f"{date_str} {req_start}", "%Y-%m-%d %H:%M")
                if target_resource.maintenance_start <= booking_dt <= target_resource.maintenance_end:
                    maintenance_ok = False
            except Exception:
                pass

        # 4. Equipment check
        res_equip = [eq.equipment_name.lower() for eq in target_resource.equipment]
        missing_equip = [eq for eq in req_equipment if eq.lower() not in res_equip]
        equipment_ok = len(missing_equip) == 0

        # 5. Overlap / Conflict check with existing bookings
        existing_bookings = db.query(Booking).filter(
            Booking.resource_id == target_resource.id,
            Booking.date == date_str,
            Booking.status.in_([BookingStatus.APPROVED, BookingStatus.RESCHEDULED])
        ).all()

        conflicts: List[BookingConflictDetail] = []
        for eb in existing_bookings:
            if current_booking_id and eb.id == current_booking_id:
                continue
            if intervals_overlap(req_start, req_end, eb.start_time, eb.end_time):
                overlap = calculate_overlap_minutes(req_start, req_end, eb.start_time, eb.end_time)
                conflicts.append(BookingConflictDetail(
                    booking_id=eb.id,
                    event_name=eb.event_name,
                    requester_name=eb.requester.name if eb.requester else "Unknown",
                    priority=eb.priority.value if hasattr(eb.priority, "value") else str(eb.priority),
                    start=eb.start_time,
                    end=eb.end_time,
                    overlap_minutes=overlap,
                    reason=f"Direct overlap of {overlap} minutes with confirmed event '{eb.event_name}'"
                ))

        time_available = len(conflicts) == 0
        overall_available = time_available and capacity_ok and operating_hours_ok and maintenance_ok

        # 6. Search Alternatives if conflict or unsuitable
        alternatives: List[AlternativeResourceCandidate] = []
        all_resources = db.query(Resource).filter(
            Resource.id != target_resource.id,
            Resource.status == ResourceStatus.ACTIVE
        ).all()

        for alt in all_resources:
            alt_equip = [eq.equipment_name.lower() for eq in alt.equipment]
            matched_count = sum(1 for eq in req_equipment if eq.lower() in alt_equip)
            equip_score = (matched_count / len(req_equipment)) if req_equipment else 1.0

            # Check if alt has conflicting bookings at requested time
            alt_bookings = db.query(Booking).filter(
                Booking.resource_id == alt.id,
                Booking.date == date_str,
                Booking.status.in_([BookingStatus.APPROVED, BookingStatus.RESCHEDULED])
            ).all()

            alt_has_conflict = any(
                intervals_overlap(req_start, req_end, b.start_time, b.end_time)
                for b in alt_bookings if not (current_booking_id and b.id == current_booking_id)
            )

            if alt.capacity >= participants:
                alternatives.append(AlternativeResourceCandidate(
                    resource_id=alt.id,
                    name=alt.name,
                    resource_type=alt.resource_type,
                    capacity=alt.capacity,
                    location=alt.location,
                    equipment_available=alt_equip,
                    equipment_match_score=round(equip_score, 2),
                    capacity_ratio=round(participants / alt.capacity, 2),
                    is_available_at_requested_time=not alt_has_conflict
                ))

        # Sort alternatives: available first, then highest equipment match, then best capacity fit
        alternatives.sort(key=lambda a: (a.is_available_at_requested_time, a.equipment_match_score, -abs(1.0 - a.capacity_ratio)), reverse=True)

        reasoning = (
            f"Analyzed resource '{target_resource.name}' for date {date_str} {req_start}-{req_end}. "
            f"Availability: {overall_available}. "
            f"Conflicts found: {len(conflicts)}. "
            f"Identified {len(alternatives)} viable alternative resources."
        )

        result = ResourceAnalysisResult(
            requested_resource=target_resource.name,
            requested_resource_id=target_resource.id,
            available=overall_available,
            capacity_ok=capacity_ok,
            operating_hours_ok=operating_hours_ok,
            maintenance_ok=maintenance_ok,
            equipment_ok=equipment_ok,
            conflicts=conflicts,
            alternatives=alternatives,
            reasoning=reasoning
        )

        duration = (time.time() - start_time_clock) * 1000
        return {
            "success": True,
            "data": result.model_dump(),
            "duration_ms": duration,
            "reasoning": reasoning
        }
