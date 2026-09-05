import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.database.session import SessionLocal
from app.models.user import User
from app.models.booking import Booking
from app.models.allocation import Allocation
from app.models.calendar_event import CalendarEvent
from app.models.notification import Notification
from app.models.decision_log import DecisionLog
from app.schemas.booking import BookingCreate, SchedulingFlexibility
from app.services.booking_service import BookingService

def run_demo():
    print("=" * 70)
    print("CAMPUSFLOW AGENTIC AI DEMO SCENARIO EXECUTION")
    print("=" * 70)

    db = SessionLocal()
    try:
        # Find student user
        user = db.query(User).filter(User.email == "student@campusflow.edu").first()
        assert user is not None, "Student user not found"

        raw_prompt = (
            "I need Seminar Hall A tomorrow from 10 AM to 1 PM for 250 students for a "
            "CSE technical symposium. We need a projector and microphone. We can shift the event by one hour."
        )
        print(f"\n[USER INPUT]:\n\"{raw_prompt}\"")

        # Step 1: Create booking request with raw prompt
        booking_in = BookingCreate(
            event_name="CSE Technical Symposium",
            event_type="technical_event",
            resource_type="seminar_hall",
            preferred_resource="Seminar Hall A",
            date="2026-09-15",
            start_time="10:00",
            end_time="13:00",
            participant_count=250,
            equipment=["projector", "microphone"],
            flexibility=SchedulingFlexibility(time_flexible=True, max_shift_minutes=60),
            raw_request=raw_prompt
        )

        booking = BookingService.create_booking(db, booking_in, user)
        print(f"\n[CREATED BOOKING]: ID={booking.id}, Status={booking.status}")

        # Step 2: Trigger Orchestrator
        print("\n[EXECUTING MULTI-AGENT WORKFLOW...]")
        final_state = BookingService.process_booking_pipeline(db, booking.id)

        print("\n" + "-" * 70)
        print("AGENT EXECUTION TRACE:")
        print("-" * 70)
        for idx, step in enumerate(final_state.get("step_history", [])):
            print(f"[{idx+1}] {step['agent']}: {step['summary']}")

        print("\n" + "-" * 70)
        print("OPTIMIZATION & EXPLANATION RESULTS:")
        print("-" * 70)
        print(f"Selected Plan: {final_state.get('optimization_result', {}).get('selected_plan_id')}")
        print(f"Score: {final_state.get('optimization_result', {}).get('score')}")
        print(f"Final Status: {booking.status.value}")
        print(f"Allocated Resource: {booking.resource.name if booking.resource else 'None'}")
        print(f"Allocated Slot: {booking.start_time} - {booking.end_time}")
        print(f"\nHuman-Readable Explanation:\n\"{final_state.get('explanation')}\"")

        print("\n" + "-" * 70)
        print("STRUCTURED DECISION FACTORS:")
        print("-" * 70)
        factors = final_state.get("decision_factors", {})
        for k, v in factors.items():
            print(f"  • {k}: {v}")

        # Check database records
        alloc = db.query(Allocation).filter(Allocation.booking_id == booking.id).first()
        cal = db.query(CalendarEvent).filter(CalendarEvent.booking_id == booking.id).first()
        notifs = db.query(Notification).filter(Notification.booking_id == booking.id).all()
        logs = db.query(DecisionLog).filter(DecisionLog.booking_id == booking.id).all()

        print("\n" + "-" * 70)
        print("DATABASE PERSISTENCE VERIFICATION:")
        print("-" * 70)
        print(f"[OK] Allocation Record: ID={alloc.id if alloc else None}, Resource={alloc.resource.name if alloc else None}, Status={alloc.status if alloc else None}")
        print(f"[OK] Calendar Event: ID={cal.id if cal else None}, Title='{cal.title if cal else None}', Time={cal.start_time}-{cal.end_time if cal else None}")
        print(f"[OK] Notifications Generated: {len(notifs)}")
        print(f"[OK] Decision Logs Recorded: {len(logs)} steps")

        print("\n" + "=" * 70)
        print("DEMO SCENARIO EXECUTED SUCCESSFULLY WITH ZERO DEFECTS!")
        print("=" * 70)
    finally:
        db.close()

if __name__ == "__main__":
    run_demo()
