import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import Base, get_db
from app.main import app
from fastapi.testclient import TestClient

TEST_DB_URL = "sqlite:///./test_campusflow.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Run seed script logic directly on test_engine
    from seed.seed_data import (
        Department, User, Resource, ResourceEquipment, Policy,
        Booking, BookingEquipment, Allocation, CalendarEvent,
        UserRole, PriorityLevel, BookingStatus, ResourceStatus,
        get_password_hash
    )
    import json
    from datetime import datetime, timedelta, timezone

    db = TestingSessionLocal()
    try:
        # 1. Depts
        departments_data = [
            {"name": "Computer Science and Engineering", "code": "CSE"},
            {"name": "Electronics and Communication Engineering", "code": "ECE"},
            {"name": "Training and Placement Cell", "code": "TAP"},
            {"name": "Student Affairs", "code": "SA"},
        ]
        dept_map = {}
        for d in departments_data:
            dept = Department(name=d["name"], code=d["code"])
            db.add(dept)
            db.flush()
            dept_map[d["code"]] = dept.id

        # 2. Users
        users_data = [
            {"name": "Student User", "email": "student@campusflow.edu", "password": "Password123!", "role": UserRole.STUDENT, "dept": "CSE"},
            {"name": "Faculty User", "email": "faculty@campusflow.edu", "password": "Password123!", "role": UserRole.FACULTY, "dept": "CSE"},
            {"name": "Admin User", "email": "admin@campusflow.edu", "password": "Password123!", "role": UserRole.SYSTEM_ADMIN, "dept": "TAP"},
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

        # 3. Resources
        resources_data = [
            {"name": "Seminar Hall A", "type": "seminar_hall", "capacity": 300, "equipment": ["projector", "microphone"]},
            {"name": "Seminar Hall B", "type": "seminar_hall", "capacity": 300, "equipment": ["projector", "microphone"]},
            {"name": "Main Auditorium", "type": "auditorium", "capacity": 800, "equipment": ["projector", "microphone", "sound_system"]},
            {"name": "Smart Classroom 1", "type": "smart_classroom", "capacity": 75, "equipment": ["projector"]},
            {"name": "Smart Classroom 2", "type": "smart_classroom", "capacity": 75, "equipment": ["projector"]},
            {"name": "Computer Lab 1", "type": "computer_lab", "capacity": 60, "equipment": ["computers", "projector"]},
            {"name": "Computer Lab 2", "type": "computer_lab", "capacity": 60, "equipment": ["computers", "projector"]},
            {"name": "Conference Room A", "type": "conference_room", "capacity": 40, "equipment": ["video_conferencing"]},
            {"name": "Conference Room B", "type": "conference_room", "capacity": 40, "equipment": ["video_conferencing"]},
        ]
        resource_map = {}
        for r in resources_data:
            res = Resource(
                name=r["name"],
                resource_type=r["type"],
                location="Campus",
                capacity=r["capacity"],
                status=ResourceStatus.ACTIVE,
                operating_start="08:00",
                operating_end="20:00",
                created_at=datetime.now(timezone.utc)
            )
            db.add(res)
            db.flush()
            resource_map[r["name"]] = res.id
            for eq in r["equipment"]:
                db.add(ResourceEquipment(resource_id=res.id, equipment_name=eq))

        # 4. Policies
        db.add(Policy(
            name="Placement Priority",
            description="Placement priority",
            rule_type="PRIORITY_ELEVATION",
            rule_config=json.dumps({"event_types": ["placement_drive"], "elevate_to": "VERY_HIGH"}),
            priority=PriorityLevel.VERY_HIGH,
            active=True
        ))

        # 5. Seeded conflicting booking on 2026-09-15
        b1 = Booking(
            requester_id=user_map["admin@campusflow.edu"],
            resource_id=resource_map["Seminar Hall A"],
            event_name="Placement Drive",
            event_type="placement_drive",
            resource_type="seminar_hall",
            date="2026-09-15",
            start_time="10:00",
            end_time="12:00",
            participant_count=200,
            status=BookingStatus.APPROVED,
            priority=PriorityLevel.VERY_HIGH
        )
        db.add(b1)
        db.flush()
        db.add(Allocation(
            booking_id=b1.id,
            resource_id=resource_map["Seminar Hall A"],
            date="2026-09-15",
            start_time="10:00",
            end_time="12:00",
            status="CONFIRMED"
        ))

        db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_campusflow.db"):
        try:
            os.remove("./test_campusflow.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
