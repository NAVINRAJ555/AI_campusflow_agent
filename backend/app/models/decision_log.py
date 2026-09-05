from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(100), nullable=False, index=True)
    input_data = Column(Text, nullable=False)   # JSON string
    output_data = Column(Text, nullable=False)  # JSON string
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    booking = relationship("Booking", back_populates="decision_logs")
