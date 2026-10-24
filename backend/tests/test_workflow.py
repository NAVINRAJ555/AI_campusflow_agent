import pytest
from app.database.session import SessionLocal
from app.models.booking import Booking
from app.models.user import User
from app.models.enums import BookingStatus
from app.orchestration.workflow import CampusFlowOrchestrator

def test_full_agent_workflow_orchestration():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        assert user is not None

        # Create a new booking request in DB
        booking = Booking(
            requester_id=user.id,
            event_name="Full Workflow Test Symposium",
            event_type="technical_event",
            resource_type="seminar_hall",
            date="2026-09-15",
            start_time="10:00",
            end_time="13:00",
            participant_count=250,
            status=BookingStatus.PROCESSING,
            time_flexible=True,
            max_shift_minutes=60,
            raw_request="I need Seminar Hall A on September 15 from 10 AM to 1 PM for 250 students for a CSE technical symposium. We need a projector and microphone. We can shift the event by one hour if required."
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        # Run orchestrator
        orchestrator = CampusFlowOrchestrator(db=db)
        state = orchestrator.run(
            booking_id=booking.id,
            raw_text=booking.raw_request,
            context={"department_name": "Computer Science and Engineering"}
        )

        assert state is not None
        assert "structured_request" in state
        assert "resource_data" in state
        assert "policy_result" in state
        assert "optimization_result" in state
        assert "explanation" in state
        assert len(state["step_history"]) >= 5

        # Check DB updated
        db.refresh(booking)
        assert booking.status in [BookingStatus.APPROVED, BookingStatus.RESCHEDULED]
        assert booking.resource_id is not None
    finally:
        if 'booking' in locals() and booking and booking.id:
            from app.models.allocation import Allocation
            from app.models.calendar_event import CalendarEvent
            from app.models.decision_log import DecisionLog
            from app.models.notification import Notification
            db.query(Allocation).filter(Allocation.booking_id == booking.id).delete()
            db.query(CalendarEvent).filter(CalendarEvent.booking_id == booking.id).delete()
            db.query(DecisionLog).filter(DecisionLog.booking_id == booking.id).delete()
            db.query(Notification).filter(Notification.booking_id == booking.id).delete()
            db.delete(booking)
            db.commit()
        db.close()
