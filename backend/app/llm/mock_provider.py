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
        
        # 1. Preferred Resource & Resource Type
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

        # 2. Date parsing (ISO YYYY-MM-DD, tomorrow, Month Day)
        today = datetime.now()
        date_val = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        
        iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        month_match = re.search(
            r"(january|february|march|april|may|june|july|august|september|october|november|december|sep|oct|nov|dec|jan|feb|mar|apr|jun|jul|aug)\s+(\d{1,2})(?:st|nd|rd|th)?",
            text_lower
        )
        
        if "tomorrow" in text_lower:
            date_val = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif iso_match:
            date_val = iso_match.group(1)
        elif month_match:
            month_str = month_match.group(1)
            day_num = int(month_match.group(2))
            month_map = {
                "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
                "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
                "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
                "nov": 11, "november": 11, "dec": 12, "december": 12
            }
            m_num = month_map.get(month_str, 9)
            date_val = f"2026-{m_num:02d}-{day_num:02d}"

        # 3. Time parsing (Supports 24h: 11:00 to 13:00, 14:00-16:00, 10:00 - 11:30; 12h: 2:00-4:00 PM, 10 AM to 1 PM)
        start_time = "10:00"
        end_time = "13:00"

        # Pattern A: 24-hour time e.g. 11:00 to 13:00 or 14:00-16:00 or 19:30 to 22:00
        time_24_match = re.search(r"(\d{1,2}):(\d{2})\s*(?:to|-|–|—)\s*(\d{1,2}):(\d{2})", text)
        # Pattern B: 12-hour time with AM/PM e.g. 10 AM to 1 PM or 2:00 to 4:00 PM or 2:00–4:00 PM
        time_12_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:to|-|–|—)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)", text, re.IGNORECASE)

        if time_24_match:
            s_h, s_m = int(time_24_match.group(1)), int(time_24_match.group(2))
            e_h, e_m = int(time_24_match.group(3)), int(time_24_match.group(4))
            start_time = f"{s_h:02d}:{s_m:02d}"
            end_time = f"{e_h:02d}:{e_m:02d}"
        elif time_12_match:
            s_h = int(time_12_match.group(1))
            s_m = int(time_12_match.group(2) or 0)
            s_mer = (time_12_match.group(3) or "").lower()
            e_h = int(time_12_match.group(4))
            e_m = int(time_12_match.group(5) or 0)
            e_mer = (time_12_match.group(6) or "").lower()

            if not s_mer:
                s_mer = e_mer if s_h <= e_h else ("am" if e_mer == "pm" else "am")

            if s_mer == "pm" and s_h < 12:
                s_h += 12
            elif s_mer == "am" and s_h == 12:
                s_h = 0

            if e_mer == "pm" and e_h < 12:
                e_h += 12
            elif e_mer == "am" and e_h == 12:
                e_h = 0

            start_time = f"{s_h:02d}:{s_m:02d}"
            end_time = f"{e_h:02d}:{e_m:02d}"

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
        if "lan" in text_lower or "internet" in text_lower or "computers" in text_lower:
            equipment.append("computers")

        # 6. Event Name & Type
        event_name = "University Academic Event"
        event_type = "department_seminar"
        if "placement" in text_lower or "interview" in text_lower or "recruitment" in text_lower:
            event_name = "Campus Placement Drive"
            event_type = "placement_drive"
        elif "exam" in text_lower or "examination" in text_lower:
            event_name = "University Examination"
            event_type = "exam"
        elif "symposium" in text_lower:
            event_name = "CSE Technical Symposium" if "cse" in text_lower else "Technical Symposium"
            event_type = "technical_event"
        elif "hackathon" in text_lower or "coding contest" in text_lower:
            event_name = "Campus Hackathon"
            event_type = "technical_event"
        elif "club" in text_lower:
            event_name = "Student Club Meeting"
            event_type = "club_meeting"
        elif "lecture" in text_lower:
            event_name = "Academic Lecture"
            event_type = "academic_lecture"
        elif "review" in text_lower or "project" in text_lower:
            event_name = "Civil Engineering Project Review" if "civil" in text_lower else "Academic Project Review"
            event_type = "academic_lecture"

        # 7. Department derivation
        dept = "General"
        if "cse" in text_lower or "computer science" in text_lower:
            dept = "Computer Science and Engineering"
        elif "civil" in text_lower:
            dept = "Civil Engineering"
        elif "mech" in text_lower or "mechanical" in text_lower:
            dept = "Mechanical Engineering"
        elif "ece" in text_lower:
            dept = "Electronics and Communication Engineering"

        # 8. Flexibility
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
            "department": dept,
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
