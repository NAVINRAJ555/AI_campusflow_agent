from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.booking import Booking
from app.models.user import User
from app.models.enums import UserRole, BookingStatus
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    AdminOverrideRequest
)
from app.services.booking_service import BookingService
from app.api.deps import get_current_user, require_roles

router = APIRouter()

def _serialize_booking(b: Booking) -> BookingResponse:
    return BookingResponse(
        id=b.id,
        requester_id=b.requester_id,
        requester_name=b.requester.name if b.requester else None,
        requester_email=b.requester.email if b.requester else None,
        department_name=b.requester.department.name if (b.requester and b.requester.department) else None,
        resource_id=b.resource_id,
        resource_name=b.resource.name if b.resource else None,
        event_name=b.event_name,
        event_type=b.event_type,
        resource_type=b.resource_type,
        date=b.date,
        start_time=b.start_time,
        end_time=b.end_time,
        participant_count=b.participant_count,
        status=b.status,
        priority=b.priority,
        time_flexible=b.time_flexible,
        max_shift_minutes=b.max_shift_minutes,
        equipment_needed=[eq.equipment_name for eq in b.equipment_needed],
        raw_request=b.raw_request,
        created_at=b.created_at,
        updated_at=b.updated_at
    )

@router.post("", response_model=BookingResponse)
def create_booking(
    booking_in: BookingCreate,
    auto_process: bool = Query(default=True, description="Immediately run the multi-agent scheduling pipeline"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = BookingService.create_booking(db, booking_in, current_user)
    if auto_process:
        BookingService.process_booking_pipeline(db, booking.id)
        db.refresh(booking)
    return _serialize_booking(booking)

@router.get("", response_model=List[BookingResponse])
def get_bookings(
    status: Optional[BookingStatus] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Booking)

    # Role-based scoping
    if current_user.role in [UserRole.STUDENT, UserRole.FACULTY]:
        query = query.filter(Booking.requester_id == current_user.id)
    elif current_user.role == UserRole.DEPARTMENT_ADMIN:
        query = query.join(Booking.requester).filter(User.department_id == current_user.department_id)

    if status:
        query = query.filter(Booking.status == status)
    if date:
        query = query.filter(Booking.date == date)

    bookings = query.order_by(Booking.created_at.desc()).all()
    return [_serialize_booking(b) for b in bookings]

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role in [UserRole.STUDENT, UserRole.FACULTY] and booking.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")

    return _serialize_booking(booking)

@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = BookingService.cancel_booking(db, booking_id, current_user)
    return _serialize_booking(booking)

@router.delete("/{booking_id}", response_model=BookingResponse)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = BookingService.cancel_booking(db, booking_id, current_user)
    return _serialize_booking(booking)

@router.post("/{booking_id}/override", response_model=BookingResponse)
def admin_override_booking(
    booking_id: int,
    override_in: AdminOverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER]))
):
    booking = BookingService.admin_override(db, booking_id, override_in, current_user)
    return _serialize_booking(booking)
