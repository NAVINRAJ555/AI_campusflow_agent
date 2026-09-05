from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base
from app.models.enums import ResourceStatus

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # auditorium, seminar_hall, lab, conference_room, classroom, bus
    location = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.ACTIVE, nullable=False)
    operating_start = Column(String(10), default="08:00", nullable=False)  # HH:MM
    operating_end = Column(String(10), default="20:00", nullable=False)    # HH:MM
    maintenance_start = Column(DateTime, nullable=True)
    maintenance_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    equipment = relationship("ResourceEquipment", back_populates="resource", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="resource")
    allocations = relationship("Allocation", back_populates="resource")
    calendar_events = relationship("CalendarEvent", back_populates="resource")

class ResourceEquipment(Base):
    __tablename__ = "resource_equipment"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    equipment_name = Column(String(50), nullable=False)

    resource = relationship("Resource", back_populates="equipment")
