from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analytics import AnalyticsOverviewResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Session = Depends(get_db)):
    return AnalyticsService.get_overview(db)

@router.get("/resource-utilization")
def get_resource_utilization(db: Session = Depends(get_db)):
    data = AnalyticsService.get_overview(db)
    return {
        "overall_utilization_rate": data.performance_metrics.resource_utilization_rate,
        "resources": data.resource_utilization
    }

@router.get("/conflicts")
def get_conflicts_analytics(db: Session = Depends(get_db)):
    data = AnalyticsService.get_overview(db)
    return {
        "conflict_resolution_rate": data.performance_metrics.conflict_resolution_rate,
        "active_conflicts": data.active_conflicts
    }

@router.get("/fairness")
def get_fairness_analytics(db: Session = Depends(get_db)):
    data = AnalyticsService.get_overview(db)
    return {
        "fairness_index": data.performance_metrics.fairness_index,
        "department_fairness": data.department_fairness
    }

@router.get("/policy-compliance")
def get_policy_compliance_analytics(db: Session = Depends(get_db)):
    data = AnalyticsService.get_overview(db)
    return {
        "policy_compliance_rate": data.performance_metrics.policy_compliance_rate
    }
