import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.booking import Booking
from app.models.negotiation import NegotiationCase, NegotiationOption
from app.models.user import User
from app.models.enums import BookingStatus
from app.models.audit_log import AuditLog
from app.models.allocation import Allocation
from app.models.calendar_event import CalendarEvent
from app.models.notification import Notification
from app.schemas.negotiation import NegotiationSelectionRequest
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/{booking_id}")
def get_negotiation_details(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    neg_case = db.query(NegotiationCase).filter(NegotiationCase.booking_id == booking_id).first()
    
    # Retrieve decision logs for negotiation if direct case record was not created
    options = []
    if neg_case:
        for opt in neg_case.options:
            options.append({
                "id": opt.id,
                "plan_data": json.loads(opt.option_data),
                "score": opt.score,
                "selected": opt.selected
            })

    return {
        "booking_id": booking.id,
        "event_name": booking.event_name,
        "requested_resource": booking.resource.name if booking.resource else booking.resource_type,
        "requested_time": f"{booking.start_time} - {booking.end_time}",
        "date": booking.date,
        "status": booking.status.value if hasattr(booking.status, "value") else str(booking.status),
        "options": options
    }

@router.post("/{booking_id}/select")
def select_negotiation_plan(
    booking_id: int,
    req: NegotiationSelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Update negotiation option selected flag
    neg_case = db.query(NegotiationCase).filter(NegotiationCase.booking_id == booking_id).first()
    if neg_case:
        neg_case.status = "RESOLVED"
        neg_case.resolved_at = datetime.now(timezone.utc)
        for opt in neg_case.options:
            data = json.loads(opt.option_data)
            if data.get("plan_id") == req.plan_id:
                opt.selected = True
                # Apply chosen allocations
                for alloc in data.get("allocations", []):
                    if alloc.get("booking_id") == booking_id:
                        booking.resource_id = alloc.get("resource_id")
                        booking.start_time = alloc.get("start_time")
                        booking.end_time = alloc.get("end_time")
                        booking.status = BookingStatus.APPROVED
            else:
                opt.selected = False

    db.add(AuditLog(
        user_id=current_user.id,
        action="NEGOTIATION_PLAN_SELECTED",
        entity_type="BOOKING",
        entity_id=str(booking_id),
        metadata_json=json.dumps({"plan_id": req.plan_id, "reason": req.admin_reason})
    ))
    db.commit()

    return {"message": f"Successfully selected plan {req.plan_id}", "booking_id": booking_id}
