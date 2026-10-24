from typing import Dict, Any, List
from app.core.config import settings

def calculate_plan_score(
    plan: Dict[str, Any],
    request_data: Dict[str, Any],
    policy_data: Dict[str, Any],
    department_usage_ratio: float = 0.5
) -> Dict[str, Any]:
    """
    Computes a transparent, weighted multi-factor optimization score for a candidate plan.
    All weights are pulled directly from settings and fully explainable.
    """
    pref_res_name = (request_data.get("preferred_resource") or "").lower()
    req_start = request_data.get("start_time")
    req_end = request_data.get("end_time")
    req_equip = [e.lower() for e in request_data.get("equipment", [])]
    participants = request_data.get("participant_count", 1)
    priority_raw = policy_data.get("priority", "MEDIUM")
    priority_str = priority_raw.value if hasattr(priority_raw, "value") else str(priority_raw).replace("PriorityLevel.", "")

    # 1. Priority factor (0.0 - 1.0)
    priority_map = {"VERY_HIGH": 1.0, "HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.25}
    priority_factor = priority_map.get(priority_str, 0.5)

    # Inspect allocations in candidate plan
    allocations = plan.get("allocations", [])
    primary_alloc = next((a for a in allocations if not a.get("is_rescheduled") or len(allocations) == 1), allocations[0] if allocations else {})

    alloc_res_name = (primary_alloc.get("resource_name") or "").lower()
    alloc_start = primary_alloc.get("start_time", req_start)
    alloc_shift = abs(primary_alloc.get("shift_minutes", 0))

    # 2. Resource match factor (0.0 - 1.0)
    if pref_res_name and pref_res_name in alloc_res_name:
        resource_match = 1.0
    else:
        # Compatible alternative
        resource_match = 0.75

    # 3. Time match factor (0.0 - 1.0)
    if alloc_shift == 0 and alloc_start == req_start:
        time_match = 1.0
    else:
        time_match = max(0.0, 1.0 - (alloc_shift / 120.0))

    # 4. Equipment match factor (0.0 - 1.0)
    equip_match = plan.get("tradeoffs", {}).get("equipment_match", 1.0)

    # 5. Utilization factor (0.0 - 1.0)
    # Higher utilization without overcrowding is optimal
    capacity = 300  # Default or extracted
    utilization_factor = min(1.0, max(0.2, participants / capacity))

    # 6. Fairness factor (0.0 - 1.0)
    # If department usage is low, fairness factor is higher
    fairness_factor = max(0.1, 1.0 - department_usage_ratio)

    # 7. Penalties
    conflict_penalty = 1.0 if not plan.get("is_physically_valid", True) else 0.0
    rescheduling_penalty = 0.0
    if plan.get("strategy") == "PREEMPTION_SWAP":
        if priority_str == "VERY_HIGH":
            rescheduling_penalty = 0.0
        elif priority_str == "HIGH":
            rescheduling_penalty = 0.1
        else:
            rescheduling_penalty = 0.5
    elif primary_alloc.get("is_rescheduled"):
        rescheduling_penalty = 0.25

    # Weighted computation
    total_score = (
        (settings.WEIGHT_PRIORITY * priority_factor)
        + (settings.WEIGHT_RESOURCE_MATCH * resource_match)
        + (settings.WEIGHT_TIME_MATCH * time_match)
        + (settings.WEIGHT_EQUIPMENT_MATCH * equip_match)
        + (settings.WEIGHT_UTILIZATION * utilization_factor)
        + (settings.WEIGHT_FAIRNESS * fairness_factor)
        - (settings.PENALTY_CONFLICT * conflict_penalty)
        - (settings.PENALTY_RESCHEDULING * rescheduling_penalty)
    )

    # Normalize to 0 - 1.0 scale
    max_possible = (
        settings.WEIGHT_PRIORITY
        + settings.WEIGHT_RESOURCE_MATCH
        + settings.WEIGHT_TIME_MATCH
        + settings.WEIGHT_EQUIPMENT_MATCH
        + settings.WEIGHT_UTILIZATION
        + settings.WEIGHT_FAIRNESS
    )
    normalized_score = round(max(0.0, total_score / max_possible), 4)

    return {
        "total_score": normalized_score,
        "raw_weighted_sum": round(total_score, 2),
        "breakdown": {
            "priority_score": round(priority_factor * settings.WEIGHT_PRIORITY, 2),
            "resource_match": round(resource_match * settings.WEIGHT_RESOURCE_MATCH, 2),
            "time_match": round(time_match * settings.WEIGHT_TIME_MATCH, 2),
            "equipment_match": round(equip_match * settings.WEIGHT_EQUIPMENT_MATCH, 2),
            "utilization": round(utilization_factor * settings.WEIGHT_UTILIZATION, 2),
            "fairness": round(fairness_factor * settings.WEIGHT_FAIRNESS, 2),
            "conflict_penalty": round(conflict_penalty * settings.PENALTY_CONFLICT, 2),
            "rescheduling_penalty": round(rescheduling_penalty * settings.PENALTY_RESCHEDULING, 2)
        }
    }
