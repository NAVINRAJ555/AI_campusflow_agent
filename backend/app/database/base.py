# Import all models here so that Base has them registered for Alembic/metadata creation
from app.database.session import Base
from app.models import (
    UserRole,
    PriorityLevel,
    BookingStatus,
    ResourceStatus,
    ConflictType,
    Department,
    User,
    Resource,
    ResourceEquipment,
    Booking,
    BookingEquipment,
    Policy,
    NegotiationCase,
    NegotiationOption,
    Allocation,
    DecisionLog,
    Notification,
    CalendarEvent,
    AuditLog,
)
