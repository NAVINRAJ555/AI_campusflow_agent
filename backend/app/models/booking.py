from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base
from app.models.enums import BookingStatus, PriorityLevel

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    event_name = Column(String(150), nullable=False)
    event_type = Column(String(50), nullable=False)  # technical_event, placement_drive, exam, department_seminar, club_meeting, administrative
    resource_type = Column(String(50), nullable=False)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    start_time = Column(String(10), nullable=False)       # HH:MM
    end_time = Column(String(10), nullable=False)         # HH:MM
    participant_count = Column(Integer, nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    priority = Column(SQLEnum(PriorityLevel), default=PriorityLevel.MEDIUM, nullable=False)
    time_flexible = Column(Boolean, default=False)
    max_shift_minutes = Column(Integer, default=0)
    raw_request = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    requester = relationship("User", back_populates="bookings")
    resource = relationship("Resource", back_populates="bookings")
    equipment_needed = relationship("BookingEquipment", back_populates="booking", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="booking", cascade="all, delete-orphan")
    decision_logs = relationship("DecisionLog", back_populates="booking", cascade="all, delete-orphan")
    negotiation_cases = relationship("NegotiationCase", back_populates="booking", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="booking", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="booking", cascade="all, delete-orphan")

class BookingEquipment(Base):
    __tablename__ = "booking_equipment"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    equipment_name = Column(String(50), nullable=False)

    booking = relationship("Booking", back_populates="equipment_needed")
