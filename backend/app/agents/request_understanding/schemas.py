from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedFlexibility(BaseModel):
    time_flexible: bool = False
    max_shift_minutes: int = 0
    alternative_dates: List[str] = []

class StructuredBookingRequest(BaseModel):
    resource_type: str = Field(description="Type of resource: auditorium, seminar_hall, lab, conference_room, classroom, bus")
    preferred_resource: Optional[str] = Field(default=None, description="Exact name of preferred resource if mentioned")
    event_name: str = Field(description="Name or title of the event")
    event_type: str = Field(description="Category: technical_event, placement_drive, exam, department_seminar, club_meeting, administrative")
    department: Optional[str] = Field(default=None, description="Department organizing the event")
    date: str = Field(description="Date in YYYY-MM-DD format")
    start_time: str = Field(description="Start time in 24-hr format HH:MM")
    end_time: str = Field(description="End time in 24-hr format HH:MM")
    participant_count: int = Field(description="Expected number of attendees/students")
    equipment: List[str] = Field(default_factory=list, description="List of required equipment e.g. projector, microphone, sound_system")
    flexibility: ExtractedFlexibility = Field(default_factory=ExtractedFlexibility)
    additional_requirements: Optional[str] = None
