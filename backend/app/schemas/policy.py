from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.models.enums import PriorityLevel

class PolicyBase(BaseModel):
    name: str
    description: str
    rule_type: str  # PRIORITY_BOOST, CAPACITY_CHECK, OPERATING_HOURS, ADVANCE_BOOKING, DEPARTMENT_RESTRICTION
    rule_config: str  # JSON formatted rule config
    priority: PriorityLevel = PriorityLevel.MEDIUM
    active: bool = True

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    rule_config: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    active: Optional[bool] = None

class PolicyResponse(PolicyBase):
    id: int

    class Config:
        from_attributes = True
