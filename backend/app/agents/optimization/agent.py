import time
from typing import Dict, Any, List, Optional
from app.agents.optimization.solver import ORToolsOptimizationSolver

class OptimizationAgent:
    """
    AGENT 5: OPTIMIZATION AGENT
    Selects the optimal allocation plan from candidate options using Google OR-Tools CP-SAT.
    Guarantees constraint satisfaction, maximizes resource utilization, and respects institutional priority.
    """

    def __init__(self):
        self.solver = ORToolsOptimizationSolver()

    def process(
        self,
        candidate_plans: List[Dict[str, Any]],
        request_data: Dict[str, Any],
        policy_data: Dict[str, Any],
        department_usage_ratio: float = 0.5
    ) -> Dict[str, Any]:
        start_time_clock = time.time()
        
        selected_plan, score, breakdown, reasoning = self.solver.solve(
            candidate_plans=candidate_plans,
            request_data=request_data,
            policy_data=policy_data,
            dept_usage_ratio=department_usage_ratio
        )

        duration = (time.time() - start_time_clock) * 1000

        if not selected_plan:
            return {
                "success": False,
                "data": {
                    "selected_plan": None,
                    "score": 0.0,
                    "allocations": [],
                    "score_breakdown": {}
                },
                "duration_ms": duration,
                "reasoning": "Constraint solver could not find any valid allocation plan."
            }

        return {
            "success": True,
            "data": {
                "selected_plan_id": selected_plan.get("plan_id"),
                "selected_plan_title": selected_plan.get("title"),
                "strategy": selected_plan.get("strategy"),
                "score": score,
                "score_breakdown": breakdown,
                "allocations": selected_plan.get("allocations", []),
                "tradeoffs": selected_plan.get("tradeoffs", {})
            },
            "duration_ms": duration,
            "reasoning": reasoning
        }
