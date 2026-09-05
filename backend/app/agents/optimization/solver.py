import logging
from typing import List, Dict, Any, Tuple, Optional
from ortools.sat.python import cp_model
from app.agents.optimization.scoring import calculate_plan_score

logger = logging.getLogger(__name__)

class ORToolsOptimizationSolver:
    """
    Solves the candidate plan selection problem using Google OR-Tools CP-SAT Solver.
    Guarantees hard constraint satisfaction and maximizes the multi-factor objective score.
    """

    def solve(
        self,
        candidate_plans: List[Dict[str, Any]],
        request_data: Dict[str, Any],
        policy_data: Dict[str, Any],
        dept_usage_ratio: float = 0.5
    ) -> Tuple[Optional[Dict[str, Any]], float, Dict[str, Any], str]:
        if not candidate_plans:
            return None, 0.0, {}, "No candidate plans available to optimize."

        # 1. Score each plan with the transparent multi-factor scoring function
        scored_plans = []
        for p in candidate_plans:
            score_result = calculate_plan_score(p, request_data, policy_data, dept_usage_ratio)
            scored_plans.append({
                "plan": p,
                "score": score_result["total_score"],
                "raw_score": int(score_result["raw_weighted_sum"] * 100), # Integer for CP-SAT
                "breakdown": score_result["breakdown"]
            })

        # 2. Build OR-Tools CP-SAT Model
        model = cp_model.CpModel()
        num_plans = len(scored_plans)
        
        # Binary selection variable x[i] in {0, 1}
        x = [model.NewBoolVar(f"select_plan_{i}") for i in range(num_plans)]

        # Hard Constraint 1: Exactly one plan must be chosen
        model.Add(sum(x) == 1)

        # Hard Constraint 2: Plans with physical conflicts or invalidity cannot be selected
        for i, sp in enumerate(scored_plans):
            if not sp["plan"].get("is_physically_valid", True):
                model.Add(x[i] == 0)

        # Objective: Maximize sum(raw_score_i * x_i)
        objective_terms = [sp["raw_score"] * x[i] for i, sp in enumerate(scored_plans)]
        model.Maximize(sum(objective_terms))

        # Solve with CP-SAT
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 5.0
        status = solver.Solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for i in range(num_plans):
                if solver.Value(x[i]) == 1:
                    chosen = scored_plans[i]
                    chosen_plan = chosen["plan"]
                    chosen_plan["score"] = chosen["score"]
                    chosen_plan["score_breakdown"] = chosen["breakdown"]
                    
                    status_name = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
                    explanation = (
                        f"Google OR-Tools CP-SAT identified {status_name} allocation plan '{chosen_plan.get('plan_id')}' "
                        f"with score {chosen['score']:.4f}. Satisfied all physical capacity and operating constraints."
                    )
                    return chosen_plan, chosen["score"], chosen["breakdown"], explanation

        # Fallback if solver finds no feasible solution (e.g. all physically invalid)
        logger.warning("OR-Tools found no feasible plan; selecting highest valid fallback.")
        valid_plans = [sp for sp in scored_plans if sp["plan"].get("is_physically_valid", True)]
        if valid_plans:
            best = max(valid_plans, key=lambda p: p["score"])
            best["plan"]["score"] = best["score"]
            best["plan"]["score_breakdown"] = best["breakdown"]
            return best["plan"], best["score"], best["breakdown"], "Selected best valid plan via fallback."

        return None, 0.0, {}, "No valid plans satisfied hard university constraints."
