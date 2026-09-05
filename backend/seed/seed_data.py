import os
import sys
import json
from datetime import datetime, timedelta, timezone

# Add parent directory to sys.path so app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models import (
    User, Department, Resource, ResourceEquipment,
    Booking, BookingEquipment, Policy, Allocation,
    CalendarEvent, Notification, AuditLog,
    UserRole, PriorityLevel, BookingStatus, ResourceStatus
)
from app.core.security import get_password_hash

def seed():
    print("Resetting and creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding Departments...")
        departments_data = [
            {"name": "Computer Science and Engineering", "code": "CSE"},
            {"name": "Electronics and Communication Engineering", "code": "ECE"},
            {"name": "Electrical and Electronics Engineering", "code": "EEE"},
            {"name": "Mechanical Engineering", "code": "MECH"},
            {"name": "Civil Engineering", "code": "CIVIL"},
            {"name": "Training and Placement Cell", "code": "TAP"},
            {"name": "Student Affairs", "code": "SA"},
        ]
        dept_map = {}
        for d in departments_data:
            dept = Department(name=d["name"], code=d["code"])
            db.add(dept)
            db.flush()
            dept_map[d["code"]] = dept.id

        print("Seeding Users for all 5 roles...")
        users_data = [
            {
                "name": "Alex Johnson (Student)",
                "email": "student@campusflow.edu",
                "password": "Password123!",
                "role": UserRole.STUDENT,
                "dept": "CSE"
            },
            {
                "name": "Dr. Sarah Mitchell (Faculty)",
                "email": "faculty@campusflow.edu",
                "password": "Password123!",
                "role": UserRole.FACULTY,
                "dept": "CSE"
            },
            {
                "name": "Prof. David Clark (Dept Admin)",
                "email": "deptadmin@campusflow.edu",
                "password": "Password123!",
                "role": UserRole.DEPARTMENT_ADMIN,
                "dept": "CSE"
            },
            {
                "name": "Robert Vance (Resource Manager)",
                "email": "manager@campusflow.edu",
                "password": "Password123!",
                "role": UserRole.RESOURCE_MANAGER,
                "dept": "SA"
            },
            {
                "name": "Admin User (System Administrator)",
                "email": "admin@campusflow.edu",
                "password": "Password123!",
                "role": UserRole.SYSTEM_ADMIN,
                "dept": "TAP"
            },
        ]
        user_map = {}
        for u in users_data:
            user = User(
                name=u["name"],
                email=u["email"],
                password_hash=get_password_hash(u["password"]),
                role=u["role"],
                department_id=dept_map[u["dept"]]
            )
            db.add(user)
            db.flush()
            user_map[u["email"]] = user.id

        print("Seeding Resources and Equipment...")
        resources_data = [
            {
                "name": "Main Auditorium",
                "type": "auditorium",
                "location": "Central Academic Block, Level 1",
                "capacity": 800,
                "start": "08:00",
                "end": "21:00",
                "equipment": ["projector", "sound_system", "microphone", "stage_lighting", "video_conferencing"]
            },
            {
                "name": "Seminar Hall A",
                "type": "seminar_hall",
                "location": "Science & Tech Wing, 2nd Floor",
                "capacity": 300,
                "start": "08:00",
                "end": "20:00",
                "equipment": ["projector", "microphone", "sound_system", "podium"]
            },
            {
                "name": "Seminar Hall B",
                "type": "seminar_hall",
                "location": "Management & Humanities Block, 1st Floor",
                "capacity": 300,
                "start": "08:00",
                "end": "20:00",
                "equipment": ["projector", "microphone", "sound_system", "smart_board"]
            },
            {
                "name": "Smart Classroom 1",
                "type": "smart_classroom",
                "location": "Tech Building, Room 204",
                "capacity": 75,
                "start": "08:00",
                "end": "19:00",
                "equipment": ["projector", "smart_board", "microphone"]
            },
            {
                "name": "Smart Classroom 2",
                "type": "smart_classroom",
                "location": "Tech Building, Room 205",
                "capacity": 75,
                "start": "08:00",
                "end": "19:00",
                "equipment": ["projector", "smart_board", "microphone"]
            },
            {
                "name": "Computer Lab 1",
                "type": "computer_lab",
                "location": "IT Center, Room 101",
                "capacity": 60,
                "start": "08:00",
                "end": "20:00",
                "equipment": ["computers", "projector", "high_speed_lan", "whiteboard"]
            },
            {
                "name": "Computer Lab 2",
                "type": "computer_lab",
                "location": "IT Center, Room 102",
                "capacity": 60,
                "start": "08:00",
                "end": "20:00",
                "equipment": ["computers", "projector", "high_speed_lan", "whiteboard"]
            },
            {
                "name": "Conference Room A",
                "type": "conference_room",
                "location": "Administration Building, 3rd Floor",
                "capacity": 40,
                "start": "08:00",
                "end": "19:00",
                "equipment": ["video_conferencing", "projector", "microphone", "oval_table"]
            },
            {
                "name": "Conference Room B",
                "type": "conference_room",
                "location": "Administration Building, 3rd Floor",
                "capacity": 40,
                "start": "08:00",
                "end": "19:00",
                "equipment": ["video_conferencing", "projector", "microphone"]
            },
        ]

        resource_map = {}
        for r in resources_data:
            res = Resource(
                name=r["name"],
                resource_type=r["type"],
                location=r["location"],
                capacity=r["capacity"],
                status=ResourceStatus.ACTIVE,
                operating_start=r["start"],
                operating_end=r["end"],
                created_at=datetime.now(timezone.utc)
            )
            db.add(res)
            db.flush()
            resource_map[r["name"]] = res.id

            for eq in r["equipment"]:
                db.add(ResourceEquipment(resource_id=res.id, equipment_name=eq))

        print("Seeding University Policies...")
        policies_data = [
            {
                "name": "Placement Activities Priority Elevation",
                "desc": "Training and Placement drives receive VERY_HIGH priority and scheduling precedence.",
                "type": "PRIORITY_ELEVATION",
                "config": json.dumps({"event_types": ["placement_drive", "placement", "interview"], "elevate_to": "VERY_HIGH"}),
                "priority": PriorityLevel.VERY_HIGH,
                "active": True
            },
            {
                "name": "University Examination Precedence",
                "desc": "Official semester and entrance examinations take non-preemptible priority.",
                "type": "PRIORITY_ELEVATION",
                "config": json.dumps({"event_types": ["exam", "examination"], "elevate_to": "VERY_HIGH"}),
                "priority": PriorityLevel.VERY_HIGH,
                "active": True
            },
            {
                "name": "Resource Capacity Enforcement",
                "desc": "Mandates that attendee count cannot exceed resource physical fire-code capacity.",
                "type": "CAPACITY_CHECK",
                "config": json.dumps({"strict": True}),
                "priority": PriorityLevel.HIGH,
                "active": True
            },
            {
                "name": "Operating Hours Compliance",
                "desc": "All events must commence and conclude strictly within the resource's operating hours.",
                "type": "OPERATING_HOURS",
                "config": json.dumps({"strict": True}),
                "priority": PriorityLevel.HIGH,
                "active": True
            },
            {
                "name": "Computer Lab Department Restriction",
                "desc": "Specialized Computer Labs are reserved primarily for CSE and IT departments.",
                "type": "DEPARTMENT_RESTRICTION",
                "config": json.dumps({"resources": ["Computer Lab 1", "Computer Lab 2"], "allowed_departments": ["Computer Science and Engineering", "CSE"]}),
                "priority": PriorityLevel.MEDIUM,
                "active": True
            },
            {
                "name": "Advance Booking Window",
                "desc": "Bookings should be submitted at least 1 day prior to event commencement.",
                "type": "ADVANCE_BOOKING",
                "config": json.dumps({"min_days_notice": 0}),
                "priority": PriorityLevel.LOW,
                "active": True
            }
        ]
        for p in policies_data:
            pol = Policy(
                name=p["name"],
                description=p["desc"],
                rule_type=p["type"],
                rule_config=p["config"],
                priority=p["priority"],
                active=p["active"]
            )
            db.add(pol)

        print("Seeding Conflicting Bookings for Demonstration...")
        # Target demo dates: tomorrow and 2026-09-15
        today = datetime.now()
        tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        sep15_str = "2026-09-15"

        dates_to_seed = [tomorrow_str, sep15_str]

        for d_str in dates_to_seed:
            # 1. Existing Confirmed Placement Drive in Seminar Hall A: 10:00 to 12:00 (Direct overlap with requested 10:00 - 13:00)
            b1 = Booking(
                requester_id=user_map["admin@campusflow.edu"],
                resource_id=resource_map["Seminar Hall A"],
                event_name="Campus Placement Drive - Google & Microsoft",
                event_type="placement_drive",
                resource_type="seminar_hall",
                date=d_str,
                start_time="10:00",
                end_time="12:00",
                participant_count=200,
                status=BookingStatus.APPROVED,
                priority=PriorityLevel.VERY_HIGH,
                time_flexible=False,
                max_shift_minutes=0,
                raw_request="Annual campus recruitment drive for final year students."
            )
            db.add(b1)
            db.flush()
            db.add(BookingEquipment(booking_id=b1.id, equipment_name="projector"))
            db.add(BookingEquipment(booking_id=b1.id, equipment_name="microphone"))

            db.add(Allocation(
                booking_id=b1.id,
                resource_id=resource_map["Seminar Hall A"],
                date=d_str,
                start_time="10:00",
                end_time="12:00",
                status="CONFIRMED"
            ))

            db.add(CalendarEvent(
                booking_id=b1.id,
                title="Campus Placement Drive - Google & Microsoft",
                date=d_str,
                start_time="10:00",
                end_time="12:00",
                resource_id=resource_map["Seminar Hall A"]
            ))

            # 2. Existing Confirmed Faculty Meeting in Conference Room A
            b2 = Booking(
                requester_id=user_map["faculty@campusflow.edu"],
                resource_id=resource_map["Conference Room A"],
                event_name="Curriculum Revision Committee",
                event_type="department_seminar",
                resource_type="conference_room",
                date=d_str,
                start_time="14:00",
                end_time="16:00",
                participant_count=25,
                status=BookingStatus.APPROVED,
                priority=PriorityLevel.MEDIUM,
                time_flexible=True,
                max_shift_minutes=30
            )
            db.add(b2)
            db.flush()
            db.add(Allocation(
                booking_id=b2.id,
                resource_id=resource_map["Conference Room A"],
                date=d_str,
                start_time="14:00",
                end_time="16:00",
                status="CONFIRMED"
            ))
            db.add(CalendarEvent(
                booking_id=b2.id,
                title="Curriculum Revision Committee",
                date=d_str,
                start_time="14:00",
                end_time="16:00",
                resource_id=resource_map["Conference Room A"]
            ))

        db.commit()
        print("Successfully seeded all realistic university data!")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
