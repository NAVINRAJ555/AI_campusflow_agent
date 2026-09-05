# CampusFlow REST API Reference

All endpoints are hosted under `/api`. OpenAPI documentation is interactively accessible at `/api/docs`.

## 1. Authentication (`/api/auth`)
- `POST /api/auth/register` - Register new user account.
- `POST /api/auth/login` - Authenticate user and receive JWT bearer token.
- `GET /api/auth/me` - Get profile and role of authenticated user.

## 2. Users (`/api/users`)
- `GET /api/users` - List all users (Admin/Resource Manager).
- `GET /api/users/{id}` - Retrieve user details.
- `PUT /api/users/{id}` - Update user role or department.
- `DELETE /api/users/{id}` - Delete user.
- `GET /api/departments` - List university departments.

## 3. Resources (`/api/resources`)
- `GET /api/resources` - List all campus venues with capacity and equipment.
- `POST /api/resources` - Create a new resource.
- `GET /api/resources/{id}` - Retrieve resource details.
- `PUT /api/resources/{id}` - Update resource, equipment, or maintenance status.
- `DELETE /api/resources/{id}` - Delete resource.
- `GET /api/resources/{id}/availability?date=YYYY-MM-DD` - Get time slots for specific venue.
- `GET /api/resources/availability?date=YYYY-MM-DD` - Get day matrix for all venues.

## 4. Bookings (`/api/bookings`)
- `POST /api/bookings?auto_process=true` - Create booking and trigger multi-agent pipeline.
- `GET /api/bookings` - List bookings (role-scoped).
- `GET /api/bookings/{id}` - Get booking details.
- `POST /api/bookings/{id}/cancel` - Cancel booking.
- `POST /api/bookings/{id}/override` - Administrative manual override (mandatory reason).

## 5. AI Assistant (`/api/ai`)
- `POST /api/ai/understand-request` - Convert natural-language prompt into structured JSON.

## 6. Scheduling & Pipeline (`/api/scheduling`)
- `POST /api/scheduling/process/{booking_id}` - Execute LangGraph multi-agent pipeline.
- `GET /api/agent-trace/{booking_id}` - Retrieve step-by-step decision history.

## 7. Negotiations (`/api/negotiations`)
- `GET /api/negotiations/{booking_id}` - Retrieve candidate plans and conflict details.
- `POST /api/negotiations/{booking_id}/select` - Select negotiation plan.

## 8. Policies (`/api/policies`)
- `GET /api/policies` - List active university policies.
- `POST /api/policies` - Create institutional policy.
- `PUT /api/policies/{id}` - Update policy configuration or active status.
- `DELETE /api/policies/{id}` - Delete policy.

## 9. Analytics (`/api/analytics`)
- `GET /api/analytics/overview` - Complete dashboard KPI summary with 8 evaluation metrics.
- `GET /api/analytics/resource-utilization` - Venue-by-venue utilization.
- `GET /api/analytics/conflicts` - Conflict resolution telemetry.
- `GET /api/analytics/fairness` - Department request satisfaction breakdown.

## 10. Notifications & Audit
- `GET /api/notifications` - Retrieve in-app notifications.
- `PUT /api/notifications/{id}/read` - Mark notification as read.
- `GET /api/calendar` - Filterable campus calendar events.
- `GET /api/audit-logs` - Immutable system audit logs.
