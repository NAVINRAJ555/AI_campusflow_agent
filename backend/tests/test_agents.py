import pytest
from app.database.session import SessionLocal
from app.models.booking import Booking
from app.models.resource import Resource
from app.agents.request_understanding import RequestUnderstandingAgent
from app.agents.resource_intelligence import ResourceIntelligenceAgent
from app.agents.policy_priority import PolicyPriorityAgent
from app.agents.negotiation import NegotiationAgent
from app.agents.optimization import OptimizationAgent
from app.agents.explanation_notification import ExplanationNotificationAgent

def test_agent_1_request_understanding():
    agent = RequestUnderstandingAgent()
    prompt = "I need Seminar Hall A on September 15 from 10 AM to 1 PM for 250 students for a CSE technical symposium. We need a projector and microphone. We can shift the event by one hour if required."
    res = agent.process(prompt)
    assert res["success"] is True
    data = res["data"]
    assert data["resource_type"] == "seminar_hall"
    assert data["preferred_resource"] == "Seminar Hall A"
    assert data["participant_count"] == 250
    assert data["start_time"] == "10:00"
    assert data["end_time"] == "13:00"
    assert "projector" in data["equipment"]
    assert "microphone" in data["equipment"]
    assert data["flexibility"]["time_flexible"] is True
    assert data["flexibility"]["max_shift_minutes"] == 60

def test_agent_2_resource_intelligence_conflict_detection():
    db = SessionLocal()
    try:
        agent = ResourceIntelligenceAgent()
        req_data = {
            "resource_type": "seminar_hall",
            "preferred_resource": "Seminar Hall A",
            "event_name": "CSE Technical Symposium",
            "date": "2026-09-15",
            "start_time": "10:00",
            "end_time": "13:00",
            "participant_count": 250,
            "equipment": ["projector", "microphone"]
        }
        res = agent.process(db, req_data)
        assert res["success"] is True
        data = res["data"]
        # Seeded booking exists from 10:00 to 12:00 in Seminar Hall A
        assert len(data["conflicts"]) > 0
        assert data["available"] is False
        assert len(data["alternatives"]) > 0
        # Seminar Hall B should be an alternative
        alt_names = [a["name"] for a in data["alternatives"]]
        assert "Seminar Hall B" in alt_names
    finally:
        db.close()

def test_agent_3_policy_and_priority():
    db = SessionLocal()
    try:
        agent = PolicyPriorityAgent()
        req_data = {
            "event_type": "technical_event",
            "event_name": "CSE Technical Symposium",
            "department": "Computer Science and Engineering",
            "date": "2026-09-15",
            "participant_count": 250
        }
        res_data = {
            "requested_resource": "Seminar Hall A",
            "capacity_ok": True,
            "operating_hours_ok": True,
            "maintenance_ok": True
        }
        res = agent.process(db, req_data, res_data)
        assert res["success"] is True
        data = res["data"]
        assert data["policy_compliant"] is True
        assert data["priority"] in ["HIGH", "VERY_HIGH"]
    finally:
        db.close()

def test_agent_4_negotiation_generates_alternatives():
    db = SessionLocal()
    try:
        agent = NegotiationAgent()
        req_data = {
            "event_name": "CSE Technical Symposium",
            "date": "2026-09-15",
            "start_time": "10:00",
            "end_time": "13:00",
            "participant_count": 250,
            "flexibility": {"time_flexible": True, "max_shift_minutes": 60}
        }
        res_analysis = {
            "requested_resource": "Seminar Hall A",
            "requested_resource_id": 2,
            "available": False,
            "conflicts": [{"booking_id": 1, "start": "10:00", "end": "12:00", "priority": "VERY_HIGH", "event_name": "Placement Drive"}],
            "alternatives": [
                {
                    "resource_id": 3,
                    "name": "Seminar Hall B",
                    "capacity": 300,
                    "equipment_match_score": 1.0,
                    "is_available_at_requested_time": True
                }
            ]
        }
        pol_data = {"priority": "HIGH", "policy_compliant": True}

        res = agent.process(db, req_data, res_analysis, pol_data, booking_id=999)
        assert res["success"] is True
        data = res["data"]
        assert data["conflict_detected"] is True
        assert len(data["candidate_plans"]) >= 2
    finally:
        db.close()

def test_agent_5_optimization_with_ortools():
    agent = OptimizationAgent()
    candidate_plans = [
        {
            "plan_id": "PLAN_1",
            "title": "Reallocate to Seminar Hall B",
            "strategy": "RESOURCE_ALTERNATIVE",
            "allocations": [
                {
                    "booking_id": 999,
                    "event_name": "CSE Symposium",
                    "resource_id": 3,
                    "resource_name": "Seminar Hall B",
                    "date": "2026-09-15",
                    "start_time": "10:00",
                    "end_time": "13:00",
                    "is_rescheduled": False,
                    "shift_minutes": 0
                }
            ],
            "is_physically_valid": True,
            "tradeoffs": {"equipment_match": 1.0}
        },
        {
            "plan_id": "PLAN_2",
            "title": "Shift Earlier in Seminar Hall A",
            "strategy": "TIME_SHIFT",
            "allocations": [
                {
                    "booking_id": 999,
                    "event_name": "CSE Symposium",
                    "resource_id": 2,
                    "resource_name": "Seminar Hall A",
                    "date": "2026-09-15",
                    "start_time": "09:00",
                    "end_time": "12:00",
                    "is_rescheduled": True,
                    "shift_minutes": -60
                }
            ],
            "is_physically_valid": True,
            "tradeoffs": {"equipment_match": 1.0}
        }
    ]
    req_data = {
        "preferred_resource": "Seminar Hall A",
        "start_time": "10:00",
        "end_time": "13:00",
        "participant_count": 250,
        "equipment": ["projector", "microphone"]
    }
    pol_data = {"priority": "HIGH"}

    res = agent.process(candidate_plans, req_data, pol_data)
    assert res["success"] is True
    data = res["data"]
    assert data["selected_plan_id"] in ["PLAN_1", "PLAN_2"]
    assert data["score"] > 0.5
    assert len(data["allocations"]) > 0

def test_agent_6_explanation_and_notification():
    db = SessionLocal()
    try:
        # Create a mock pending booking
        booking = Booking(
            requester_id=1,
            event_name="Test Event For Explanation",
            event_type="technical_event",
            resource_type="seminar_hall",
            date="2026-09-15",
            start_time="10:00",
            end_time="13:00",
            participant_count=250,
            status="PENDING",
            priority="HIGH"
        )
        db.add(booking)
        db.commit()

        agent = ExplanationNotificationAgent()
        req_data = {
            "preferred_resource": "Seminar Hall A",
            "resource_type": "seminar_hall",
            "date": "2026-09-15",
            "start_time": "10:00",
            "end_time": "13:00",
            "participant_count": 250,
            "equipment": ["projector", "microphone"]
        }
        res_analysis = {
            "requested_resource": "Seminar Hall A",
            "conflicts": [{"event_name": "Placement Drive", "start": "10:00", "end": "12:00"}]
        }
        pol_res = {"priority": "HIGH"}
        opt_res = {
            "selected_plan_id": "PLAN_1",
            "strategy": "RESOURCE_ALTERNATIVE",
            "score": 0.88,
            "allocations": [
                {
                    "booking_id": booking.id,
                    "event_name": "Test Event For Explanation",
                    "resource_id": 3,
                    "resource_name": "Seminar Hall B",
                    "date": "2026-09-15",
                    "start_time": "10:00",
                    "end_time": "13:00",
                    "is_rescheduled": False,
                    "shift_minutes": 0
                }
            ]
        }

        res = agent.process(
            db=db,
            booking_id=booking.id,
            request_data=req_data,
            resource_analysis=res_analysis,
            policy_result=pol_res,
            negotiation_result={},
            optimization_result=opt_res
        )

        assert res["success"] is True
        data = res["data"]
        assert "Seminar Hall B" in data["human_readable_explanation"]
        assert data["decision_factors"]["decision"] == "REALLOCATED"
        assert len(data["notifications"]) > 0

        # Verify DB was updated
        db.refresh(booking)
        assert booking.status.value in ["APPROVED", "RESCHEDULED"]
        assert booking.resource_id == 3
    finally:
        db.close()
