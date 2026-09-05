from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.resource import Resource
from app.models.user import User
from app.models.enums import ResourceStatus, UserRole
from app.schemas.resource import (
    ResourceResponse,
    ResourceCreate,
    ResourceUpdate,
    ResourceAvailabilityResponse
)
from app.services.resource_service import ResourceService
from app.api.deps import get_current_user, require_roles

router = APIRouter()

def _serialize_resource(r: Resource) -> ResourceResponse:
    return ResourceResponse(
        id=r.id,
        name=r.name,
        resource_type=r.resource_type,
        location=r.location,
        capacity=r.capacity,
        operating_start=r.operating_start,
        operating_end=r.operating_end,
        status=r.status,
        equipment=[eq.equipment_name for eq in r.equipment],
        maintenance_start=r.maintenance_start,
        maintenance_end=r.maintenance_end,
        created_at=r.created_at
    )

@router.get("", response_model=List[ResourceResponse])
def get_resources(
    resource_type: Optional[str] = None,
    status: Optional[ResourceStatus] = None,
    db: Session = Depends(get_db)
):
    resources = ResourceService.get_all(db, resource_type, status)
    return [_serialize_resource(r) for r in resources]

@router.post("", response_model=ResourceResponse)
def create_resource(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER]))
):
    res = ResourceService.create(db, resource_in)
    return _serialize_resource(res)

@router.get("/availability")
def get_all_availability(
    date: str = Query(default=datetime.now().strftime("%Y-%m-%d")),
    db: Session = Depends(get_db)
):
    resources = ResourceService.get_all(db)
    return [
        ResourceService.get_availability(db, r.id, date)
        for r in resources
    ]

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    res = ResourceService.get_by_id(db, resource_id)
    return _serialize_resource(res)

@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource_in: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER]))
):
    res = ResourceService.update(db, resource_id, resource_in)
    return _serialize_resource(res)

@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER]))
):
    ResourceService.delete(db, resource_id)
    return {"message": "Resource deleted successfully"}

@router.get("/{resource_id}/availability", response_model=ResourceAvailabilityResponse)
def get_resource_availability(
    resource_id: int,
    date: str = Query(default=datetime.now().strftime("%Y-%m-%d")),
    db: Session = Depends(get_db)
):
    return ResourceService.get_availability(db, resource_id, date)
