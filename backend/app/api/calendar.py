from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.calendar_event import CalendarEvent
from app.models.booking import Booking
from app.models.resource import Resource
from app.models.department import Department
from app.models.enums import BookingStatus

router = APIRouter()

@router.get("")
def get_calendar_events(
    resource_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    department_id: Optional[int] = None,
    date: Optional[str] = None,
    status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CalendarEvent).join(CalendarEvent.booking).join(CalendarEvent.resource)

    if resource_id:
        query = query.filter(CalendarEvent.resource_id == resource_id)
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if department_id:
        query = query.filter(Booking.requester.has(department_id=department_id))
    if date:
        query = query.filter(CalendarEvent.date == date)
    if status:
        query = query.filter(Booking.status == status)

    events = query.all()
    res = []
    for ev in events:
        b = ev.booking
        r = ev.resource
        dept_name = b.requester.department.name if (b and b.requester and b.requester.department) else "General"
        res.append({
            "id": ev.id,
            "booking_id": ev.booking_id,
            "title": ev.title,
            "event_name": b.event_name if b else ev.title,
            "resource_id": ev.resource_id,
            "resource_name": r.name if r else "Unknown",
            "resource_type": r.resource_type if r else "Unknown",
            "date": ev.date,
            "start_time": ev.start_time,
            "end_time": ev.end_time,
            "department_name": dept_name,
            "status": b.status.value if (b and hasattr(b.status, "value")) else "APPROVED",
            "priority": b.priority.value if (b and hasattr(b.priority, "value")) else "MEDIUM"
        })
    return res
