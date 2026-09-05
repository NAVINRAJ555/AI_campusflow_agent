# CampusFlow System Architecture

CampusFlow is an Agentic AI-based university resource management and scheduling platform. It replaces traditional First-Come-First-Serve (FCFS) allocation with an intelligent multi-agent pipeline: **Understand → Check → Prioritize → Negotiate → Optimize → Explain**.

```mermaid
graph TD
    User([User: Student / Faculty / Admin]) -->|Natural Language / Form| WebUI[React 18 + Vite + Tailwind CSS]
    WebUI -->|REST API + JWT| FastAPI[FastAPI Backend Gateway]
    
    subgraph Auth & Access
        FastAPI --> RBAC[Role-Based Authorization]
    end
    
    FastAPI --> BookingService[Booking Service]
    BookingService --> Orchestrator[LangGraph Stateful Multi-Agent Orchestrator]
    
    subgraph Multi-Agent Execution Pipeline
        Orchestrator --> A1[Agent 1: Request Understanding]
        A1 --> A2[Agent 2: Resource Intelligence]
        A2 --> A3[Agent 3: Policy & Priority]
        A3 --> CheckConflict{Conflict Detected?}
        CheckConflict -- YES --> A4[Agent 4: Multi-Alternative Negotiation]
        CheckConflict -- NO --> A5[Agent 5: Google OR-Tools Optimization]
        A4 --> A5
        A5 --> A6[Agent 6: Explanation & Notification]
    end
    
    subgraph Data & Persistence Layer
        A2 <--> DB[(PostgreSQL / SQLite Database)]
        A3 <--> Policies[(Policies Table)]
        A5 <--> Weights[Configurable Multi-Factor Weights]
        A6 --> DecisionLogs[(Decision & Audit Logs)]
        A6 --> Calendar[(Calendar Events)]
        A6 --> Notifs[(In-App Notifications)]
    end
```

## Architectural Highlights
1. **Separation of Concerns**:
   - The LLM reasons about qualitative aspects and semantic requests.
   - Deterministic constraint layers (Resource Intelligence, Policy Engine, and Google OR-Tools) handle physical capacity, temporal overlaps, and mathematical optimization.
2. **Stateful Orchestration**:
   - Orchestrated via LangGraph `StateGraph(BookingWorkflowState)` with conditional branching based on detected conflicts.
3. **Transparent Explainability**:
   - Every decision stores structured decision factors (priority, capacity, time, equipment, conflict, fairness, final reason) in `DECISION_LOGS`.
4. **Administrative Oversight**:
   - Administrative users can manually override AI allocations with a mandatory audit reason.
