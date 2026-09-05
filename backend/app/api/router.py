from fastapi import APIRouter
from app.api import (
    auth,
    users,
    resources,
    bookings,
    ai,
    scheduling,
    negotiations,
    policies,
    analytics,
    notifications,
    agent_trace,
    audit_logs,
    calendar,
    departments
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Booking"])
api_router.include_router(scheduling.router, prefix="/scheduling", tags=["Scheduling"])
api_router.include_router(negotiations.router, prefix="/negotiations", tags=["Negotiations"])
api_router.include_router(policies.router, prefix="/policies", tags=["Policies"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(agent_trace.router, prefix="/agent-trace", tags=["Agent Trace"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
