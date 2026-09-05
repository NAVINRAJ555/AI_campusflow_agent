from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.auth import UserResponse, UserUpdate
from app.core.security import get_password_hash
from app.api.deps import get_current_user, require_roles

router = APIRouter()

@router.get("", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER]))
):
    users = db.query(User).all()
    return [
        UserResponse(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            department_id=u.department_id,
            department_name=u.department.name if u.department else None,
            created_at=u.created_at
        )
        for u in users
    ]

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.SYSTEM_ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        department_id=user.department_id,
        department_name=user.department.name if user.department else None,
        created_at=user.created_at
    )

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.name is not None:
        user.name = user_in.name
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.password is not None:
        user.password_hash = get_password_hash(user_in.password)
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.department_id is not None:
        user.department_id = user_in.department_id

    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        department_id=user.department_id,
        department_name=user.department.name if user.department else None,
        created_at=user.created_at
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
