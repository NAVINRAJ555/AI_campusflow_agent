# CampusFlow Demonstration Scenarios

This document outlines the five working demonstration scenarios implemented and verified in CampusFlow.

---

### SCENARIO 1: Direct Approval (No Conflict)
- **Input**:
  `"I need Conference Room B on September 15 from 10:00 AM to 11:30 AM for 15 students for a Civil Engineering project review. We need a projector."`
- **Workflow Path**:
  Understand $\rightarrow$ Resource Intelligence (Available = True) $\rightarrow$ Policy & Priority (Compliant = True, Priority = MEDIUM) $\rightarrow$ Optimization (Direct Plan) $\rightarrow$ Explanation & Notification.
- **Expected Outcome**:
  Direct `APPROVED` status. Calendar event and notification dispatched instantly.

---

### SCENARIO 2: Resource Conflict & Negotiation (Mandatory Demo Scenario)
- **Input**:
  `"I need Seminar Hall A tomorrow from 10 AM to 1 PM for 250 students for a CSE technical symposium. We need a projector and microphone. We can shift the event by one hour."`
- **Initial State**:
  Seminar Hall A has an existing confirmed booking ("Campus Placement Drive" from 10:00 AM to 12:00 PM).
- **Workflow Path**:
  Understand $\rightarrow$ Resource Intelligence (Conflict Detected: 120-minute direct overlap) $\rightarrow$ Policy & Priority (High Priority) $\rightarrow$ Negotiation Agent (Synthesizes 3 candidate plans) $\rightarrow$ Google OR-Tools CP-SAT (Selects optimal plan) $\rightarrow$ Explanation Agent.
- **Expected Outcome**:
  Reallocated to a suitable alternative (e.g. Main Auditorium or Seminar Hall B) or time-shifted, preserving participant count (250) and equipment. Structured explanation generated with exact conflict details.

---

### SCENARIO 3: Physical Capacity Violation
- **Input**:
  `"I need Conference Room A on September 15 from 2 PM to 4 PM for 150 students for a lecture."`
- **Conflict**:
  Conference Room A physical capacity is 40 seats.
- **Workflow Path**:
  Resource Intelligence detects `capacity_ok = False` $\rightarrow$ Policy & Priority flags `CAPACITY_CHECK` violation $\rightarrow$ Negotiation Agent filters for alternatives with capacity $\ge 150$ (e.g. Seminar Hall A or Main Auditorium) $\rightarrow$ Optimization selects appropriate hall.
- **Expected Outcome**:
  Venue substituted with a capable hall or rejected with clear capacity explanation.

---

### SCENARIO 4: Institutional Policy Restriction
- **Input**:
  `"Student club meeting in Computer Lab 1 on September 15 from 11 AM to 1 PM."`
- **Policy Evaluated**:
  `DEPARTMENT_RESTRICTION` policy on Computer Lab 1 (restricted to CSE/IT coursework).
- **Workflow Path**:
  Policy Agent evaluates student club request vs active policy $\rightarrow$ Detects violation.
- **Expected Outcome**:
  Policy violation detected with formal rule citation in the explanation and agent trace.

---

### SCENARIO 5: Multiple Competing Priority Requests
- **Competing Requests**:
  1. *Request A*: Student Club General Meeting (Priority: LOW, requested Seminar Hall A at 10 AM).
  2. *Request B*: University Placement Drive (Priority: VERY_HIGH, requested Seminar Hall A at 10 AM).
- **Workflow Path**:
  Negotiation Agent generates candidate plans including priority preemption swap $\rightarrow$ Optimization assigns higher priority weight ($w_{\text{priority}} \times 1.0$) to Placement Drive $\rightarrow$ Relocates lower-priority Club Meeting to alternative room.
- **Expected Outcome**:
  Placement Drive awarded primary resource; Student Club rescheduled with full notification and audit explanation.
