from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.booking import Booking
from app.models.user import User
from app.services.booking_service import BookingService
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/process/{booking_id}")
def process_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    final_state = BookingService.process_booking_pipeline(db, booking_id)
    return {
        "booking_id": booking_id,
        "status": final_state.get("final_decision", {}).get("decision_factors", {}).get("decision", "PROCESSED"),
        "explanation": final_state.get("explanation"),
        "decision_factors": final_state.get("decision_factors"),
        "step_history": final_state.get("step_history", [])
    }
