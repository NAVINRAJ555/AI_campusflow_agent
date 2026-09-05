import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.booking import Booking, BookingEquipment
from app.models.resource import Resource
from app.models.user import User
from app.models.enums import BookingStatus, PriorityLevel, UserRole
from app.models.allocation import Allocation
from app.models.calendar_event import CalendarEvent
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.schemas.booking import BookingCreate, BookingUpdate, AdminOverrideRequest
from app.orchestration.workflow import CampusFlowOrchestrator

class BookingService:
    @staticmethod
    def create_booking(db: Session, booking_in: BookingCreate, requester: User) -> Booking:
        # Resolve resource if preferred_resource provided
        target_resource = None
        if booking_in.preferred_resource:
            target_resource = db.query(Resource).filter(Resource.name.ilike(f"%{booking_in.preferred_resource}%")).first()
        elif booking_in.resource_type:
            target_resource = db.query(Resource).filter(Resource.resource_type == booking_in.resource_type).first()

        booking = Booking(
            requester_id=requester.id,
            resource_id=target_resource.id if target_resource else None,
            event_name=booking_in.event_name,
            event_type=booking_in.event_type,
            resource_type=booking_in.resource_type,
            date=booking_in.date,
            start_time=booking_in.start_time,
            end_time=booking_in.end_time,
            participant_count=booking_in.participant_count,
            status=BookingStatus.PROCESSING,
            priority=PriorityLevel.MEDIUM,
            time_flexible=booking_in.flexibility.time_flexible,
            max_shift_minutes=booking_in.flexibility.max_shift_minutes,
            raw_request=booking_in.raw_request or f"Requested {booking_in.event_name} on {booking_in.date}"
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        # Add equipment requirements
        for eq_name in booking_in.equipment:
            db.add(BookingEquipment(booking_id=booking.id, equipment_name=eq_name))
        db.commit()

        # Audit log creation
        db.add(AuditLog(
            user_id=requester.id,
            action="CREATE_BOOKING",
            entity_type="BOOKING",
            entity_id=str(booking.id),
            metadata_json=json.dumps({"event_name": booking.event_name, "date": booking.date})
        ))
        db.commit()

        return booking

    @staticmethod
    def process_booking_pipeline(db: Session, booking_id: int) -> Dict[str, Any]:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")

        orchestrator = CampusFlowOrchestrator(db=db)
        context = {
            "department_name": booking.requester.department.name if (booking.requester and booking.requester.department) else "General",
            "requester_role": booking.requester.role.value if booking.requester else "STUDENT"
        }

        final_state = orchestrator.run(
            booking_id=booking.id,
            raw_text=booking.raw_request,
            context=context
        )
        return final_state

    @staticmethod
    def admin_override(db: Session, booking_id: int, override_in: AdminOverrideRequest, admin_user: User) -> Booking:
        if admin_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER]:
            raise HTTPException(status_code=403, detail="Only Admins and Resource Managers can perform overrides.")

        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        target_resource = db.query(Resource).filter(Resource.id == override_in.resource_id).first()
        if not target_resource:
            raise HTTPException(status_code=404, detail="Target resource not found")

        # Update booking details
        prev_resource = booking.resource.name if booking.resource else "None"
        prev_time = f"{booking.start_time}-{booking.end_time}"

        booking.resource_id = target_resource.id
        booking.date = override_in.date
        booking.start_time = override_in.start_time
        booking.end_time = override_in.end_time
        booking.status = BookingStatus.APPROVED
        booking.updated_at = datetime.now(timezone.utc)

        # Update allocation
        db.query(Allocation).filter(Allocation.booking_id == booking_id).delete()
        db.add(Allocation(
            booking_id=booking.id,
            resource_id=target_resource.id,
            date=override_in.date,
            start_time=override_in.start_time,
            end_time=override_in.end_time,
            status="MANUAL_OVERRIDE"
        ))

        # Update Calendar
        db.query(CalendarEvent).filter(CalendarEvent.booking_id == booking_id).delete()
        db.add(CalendarEvent(
            booking_id=booking.id,
            title=f"{booking.event_name} (Manual Admin Allocation)",
            date=override_in.date,
            start_time=override_in.start_time,
            end_time=override_in.end_time,
            resource_id=target_resource.id
        ))

        # Notify user
        db.add(Notification(
            user_id=booking.requester_id,
            booking_id=booking.id,
            message=f"Administrator {admin_user.name} manually updated your booking for '{booking.event_name}' to {target_resource.name} ({override_in.start_time} - {override_in.end_time}). Reason: {override_in.reason}",
            type="RESCHEDULED",
            is_read=False
        ))

        # Audit log
        db.add(AuditLog(
            user_id=admin_user.id,
            action="ADMIN_MANUAL_OVERRIDE",
            entity_type="BOOKING",
            entity_id=str(booking.id),
            metadata_json=json.dumps({
                "admin_name": admin_user.name,
                "reason": override_in.reason,
                "previous_resource": prev_resource,
                "previous_time": prev_time,
                "new_resource": target_resource.name,
                "new_time": f"{override_in.start_time}-{override_in.end_time}"
            })
        ))

        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def cancel_booking(db: Session, booking_id: int, user: User) -> Booking:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Check permissions: owner or admin
        if user.role not in [UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER] and booking.requester_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

        booking.status = BookingStatus.CANCELLED
        booking.updated_at = datetime.now(timezone.utc)

        # Remove allocation and calendar entries
        db.query(Allocation).filter(Allocation.booking_id == booking_id).delete()
        db.query(CalendarEvent).filter(CalendarEvent.booking_id == booking_id).delete()

        db.add(Notification(
            user_id=booking.requester_id,
            booking_id=booking.id,
            message=f"Your booking for '{booking.event_name}' on {booking.date} has been cancelled.",
            type="INFO",
            is_read=False
        ))

        db.add(AuditLog(
            user_id=user.id,
            action="CANCEL_BOOKING",
            entity_type="BOOKING",
            entity_id=str(booking.id),
            metadata_json=json.dumps({"cancelled_by": user.name})
        ))

        db.commit()
        db.refresh(booking)
        return booking
