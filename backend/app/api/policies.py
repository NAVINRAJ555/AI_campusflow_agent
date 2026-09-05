from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.policy import Policy
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter()

@router.get("", response_model=List[PolicyResponse])
def get_policies(db: Session = Depends(get_db)):
    policies = db.query(Policy).all()
    return policies

@router.post("", response_model=PolicyResponse)
def create_policy(
    policy_in: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    policy = Policy(
        name=policy_in.name,
        description=policy_in.description,
        rule_type=policy_in.rule_type,
        rule_config=policy_in.rule_config,
        priority=policy_in.priority,
        active=policy_in.active
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy

@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: int,
    policy_in: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy_in.name is not None:
        policy.name = policy_in.name
    if policy_in.description is not None:
        policy.description = policy_in.description
    if policy_in.rule_type is not None:
        policy.rule_type = policy_in.rule_type
    if policy_in.rule_config is not None:
        policy.rule_config = policy_in.rule_config
    if policy_in.priority is not None:
        policy.priority = policy_in.priority
    if policy_in.active is not None:
        policy.active = policy_in.active

    db.commit()
    db.refresh(policy)
    return policy

@router.delete("/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()
    return {"message": "Policy deleted successfully"}
