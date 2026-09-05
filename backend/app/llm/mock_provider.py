import re
import json
from datetime import datetime, timedelta
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from app.llm.provider import LLMProvider

T = TypeVar("T", bound=BaseModel)

class MockLLMProvider(LLMProvider):
    """
    Deterministic Mock LLM Provider that executes real parsing and reasoning logic
    without requiring external API keys.
    """

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        prompt_lower = prompt.lower()
        if "explain" in prompt_lower or "explanation" in prompt_lower:
            return (
                "Your booking request has been evaluated through the multi-agent negotiation pipeline. "
                "Due to priority and capacity requirements, the optimal resource has been allocated to ensure "
                "maximum campus utilization and fairness."
            )
        return "Deterministic agent reasoning completed successfully."

    def generate_structured(self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None) -> T:
        data = self._parse_to_schema(prompt, schema_cls)
        return schema_cls.model_validate(data)

    def _parse_to_schema(self, prompt: str, schema_cls: Type[T]) -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Check if schema looks like StructuredBookingRequest
        fields = schema_cls.model_fields.keys() if hasattr(schema_cls, "model_fields") else []

        if "resource_type" in fields and "event_name" in fields:
            return self._parse_booking_request(prompt)
        
        # Default fallback
        return {}

    def _parse_booking_request(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # 1. Preferred Resource
        preferred_resource = None
        resource_type = "seminar_hall"
        if "seminar hall a" in text_lower:
            preferred_resource = "Seminar Hall A"
            resource_type = "seminar_hall"
        elif "seminar hall b" in text_lower:
            preferred_resource = "Seminar Hall B"
            resource_type = "seminar_hall"
        elif "main auditorium" in text_lower or "auditorium" in text_lower:
            preferred_resource = "Main Auditorium"
            resource_type = "auditorium"
        elif "computer lab 1" in text_lower:
            preferred_resource = "Computer Lab 1"
            resource_type = "computer_lab"
        elif "computer lab 2" in text_lower:
            preferred_resource = "Computer Lab 2"
            resource_type = "computer_lab"
        elif "conference room a" in text_lower:
            preferred_resource = "Conference Room A"
            resource_type = "conference_room"
        elif "conference room b" in text_lower:
            preferred_resource = "Conference Room B"
            resource_type = "conference_room"
        elif "smart classroom 1" in text_lower or "classroom 1" in text_lower:
            preferred_resource = "Smart Classroom 1"
            resource_type = "smart_classroom"
        elif "smart classroom 2" in text_lower or "classroom 2" in text_lower:
            preferred_resource = "Smart Classroom 2"
            resource_type = "smart_classroom"

        # 2. Date parsing
        today = datetime.now()
        date_val = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        if "tomorrow" in text_lower:
            date_val = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "september 15" in text_lower or "sep 15" in text_lower:
            date_val = "2026-09-15"
        else:
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
            if date_match:
                date_val = date_match.group(1)

        # 3. Time parsing
        start_time = "10:00"
        end_time = "13:00"
        time_match = re.search(r"(\d{1,2})\s*(am|pm)?\s*(to|-)\s*(\d{1,2})\s*(am|pm)", text, re.IGNORECASE)
        if time_match:
            s_hr = int(time_match.group(1))
            s_mer = (time_match.group(2) or "").lower()
            e_hr = int(time_match.group(4))
            e_mer = (time_match.group(5) or "").lower()
            
            # If start meridian missing, infer from end meridian or hour
            if not s_mer:
                s_mer = e_mer if s_hr <= e_hr else ("am" if e_mer == "pm" else "am")
            
            if s_mer == "pm" and s_hr < 12:
                s_hr += 12
            elif s_mer == "am" and s_hr == 12:
                s_hr = 0

            if e_mer == "pm" and e_hr < 12:
                e_hr += 12
            elif e_mer == "am" and e_hr == 12:
                e_hr = 0

            start_time = f"{s_hr:02d}:00"
            end_time = f"{e_hr:02d}:00"

        # 4. Participant Count
        participant_count = 100
        count_match = re.search(r"(\d+)\s+(?:students|participants|people|attendees|persons)", text_lower)
        if not count_match:
            count_match = re.search(r"for\s+(\d+)", text_lower)
        if count_match:
            participant_count = int(count_match.group(1))

        # 5. Equipment
        equipment = []
        if "projector" in text_lower:
            equipment.append("projector")
        if "microphone" in text_lower or "mic" in text_lower:
            equipment.append("microphone")
        if "sound" in text_lower or "speaker" in text_lower:
            equipment.append("sound_system")
        if "video" in text_lower or "recording" in text_lower:
            equipment.append("video_conferencing")

        # 6. Event Name & Type
        event_name = "University Academic Event"
        event_type = "department_seminar"
        if "symposium" in text_lower:
            event_name = "CSE Technical Symposium" if "cse" in text_lower else "Technical Symposium"
            event_type = "technical_event"
        elif "placement" in text_lower or "interview" in text_lower:
            event_name = "Campus Placement Drive"
            event_type = "placement_drive"
        elif "exam" in text_lower:
            event_name = "University Examination"
            event_type = "exam"
        elif "hackathon" in text_lower:
            event_name = "Campus Hackathon"
            event_type = "technical_event"
        elif "club" in text_lower:
            event_name = "Student Club Meeting"
            event_type = "club_meeting"

        # 7. Flexibility
        time_flexible = False
        max_shift_minutes = 0
        if "shift" in text_lower or "flexible" in text_lower or "move" in text_lower:
            time_flexible = True
            shift_match = re.search(r"(\d+)\s*(hour|hours|hr|hrs|minute|minutes|min|mins)", text_lower)
            if shift_match:
                val = int(shift_match.group(1))
                unit = shift_match.group(2)
                if "hour" in unit or "hr" in unit:
                    max_shift_minutes = val * 60
                else:
                    max_shift_minutes = val
            else:
                max_shift_minutes = 60

        return {
            "resource_type": resource_type,
            "preferred_resource": preferred_resource or "Seminar Hall A",
            "event_name": event_name,
            "event_type": event_type,
            "department": "Computer Science and Engineering",
            "date": date_val,
            "start_time": start_time,
            "end_time": end_time,
            "participant_count": participant_count,
            "equipment": equipment,
            "flexibility": {
                "time_flexible": time_flexible,
                "max_shift_minutes": max_shift_minutes,
                "alternative_dates": []
            },
            "additional_requirements": text
        }
