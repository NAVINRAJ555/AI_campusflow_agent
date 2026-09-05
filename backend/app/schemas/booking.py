from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.enums import BookingStatus, PriorityLevel

class SchedulingFlexibility(BaseModel):
    time_flexible: bool = False
    max_shift_minutes: int = 0
    alternative_dates: List[str] = []

class BookingCreate(BaseModel):
    event_name: str
    event_type: str  # technical_event, placement_drive, exam, department_seminar, club_meeting, administrative
    resource_type: str
    preferred_resource: Optional[str] = None
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    participant_count: int
    equipment: List[str] = []
    flexibility: SchedulingFlexibility = Field(default_factory=SchedulingFlexibility)
    additional_requirements: Optional[str] = None
    raw_request: Optional[str] = None

class BookingUpdate(BaseModel):
    event_name: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    participant_count: Optional[int] = None
    status: Optional[BookingStatus] = None
    priority: Optional[PriorityLevel] = None

class AdminOverrideRequest(BaseModel):
    resource_id: int
    date: str
    start_time: str
    end_time: str
    reason: str

class BookingResponse(BaseModel):
    id: int
    requester_id: int
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    department_name: Optional[str] = None
    resource_id: Optional[int] = None
    resource_name: Optional[str] = None
    event_name: str
    event_type: str
    resource_type: str
    date: str
    start_time: str
    end_time: str
    participant_count: int
    status: BookingStatus
    priority: PriorityLevel
    time_flexible: bool
    max_shift_minutes: int
    equipment_needed: List[str] = []
    raw_request: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NaturalLanguageBookingRequest(BaseModel):
    prompt: str
    department_id: Optional[int] = None
