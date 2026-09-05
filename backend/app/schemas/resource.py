from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.enums import ResourceStatus

class ResourceBase(BaseModel):
    name: str
    resource_type: str
    location: str
    capacity: int
    operating_start: str = "08:00"
    operating_end: str = "20:00"
    status: ResourceStatus = ResourceStatus.ACTIVE

class ResourceCreate(ResourceBase):
    equipment: List[str] = []
    maintenance_start: Optional[datetime] = None
    maintenance_end: Optional[datetime] = None

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    resource_type: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    operating_start: Optional[str] = None
    operating_end: Optional[str] = None
    status: Optional[ResourceStatus] = None
    equipment: Optional[List[str]] = None
    maintenance_start: Optional[datetime] = None
    maintenance_end: Optional[datetime] = None

class ResourceResponse(ResourceBase):
    id: int
    equipment: List[str] = []
    maintenance_start: Optional[datetime] = None
    maintenance_end: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    is_available: bool
    booking_id: Optional[int] = None
    event_name: Optional[str] = None

class ResourceAvailabilityResponse(BaseModel):
    resource_id: int
    resource_name: str
    date: str
    operating_start: str
    operating_end: str
    status: ResourceStatus
    is_operational: bool
    maintenance_reason: Optional[str] = None
    booked_slots: List[TimeSlot]
    available_slots: List[TimeSlot]
