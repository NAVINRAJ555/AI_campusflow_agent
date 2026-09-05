from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    date = Column(String(10), nullable=False, index=True)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)

    booking = relationship("Booking", back_populates="calendar_events")
    resource = relationship("Resource", back_populates="calendar_events")
