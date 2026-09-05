from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.resource import Resource, ResourceEquipment
from app.models.booking import Booking
from app.models.enums import ResourceStatus, BookingStatus
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceAvailabilityResponse, TimeSlot
from app.agents.resource_intelligence.agent import time_to_minutes

class ResourceService:
    @staticmethod
    def get_all(db: Session, resource_type: Optional[str] = None, status: Optional[ResourceStatus] = None) -> List[Resource]:
        query = db.query(Resource)
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
        if status:
            query = query.filter(Resource.status == status)
        return query.all()

    @staticmethod
    def get_by_id(db: Session, resource_id: int) -> Resource:
        res = db.query(Resource).filter(Resource.id == resource_id).first()
        if not res:
            raise HTTPException(status_code=404, detail="Resource not found")
        return res

    @staticmethod
    def create(db: Session, data: ResourceCreate) -> Resource:
        res = Resource(
            name=data.name,
            resource_type=data.resource_type,
            location=data.location,
            capacity=data.capacity,
            status=data.status,
            operating_start=data.operating_start,
            operating_end=data.operating_end,
            maintenance_start=data.maintenance_start,
            maintenance_end=data.maintenance_end,
            created_at=datetime.now(timezone.utc)
        )
        db.add(res)
        db.commit()
        db.refresh(res)

        for eq in data.equipment:
            db.add(ResourceEquipment(resource_id=res.id, equipment_name=eq))
        db.commit()
        db.refresh(res)
        return res

    @staticmethod
    def update(db: Session, resource_id: int, data: ResourceUpdate) -> Resource:
        res = ResourceService.get_by_id(db, resource_id)
        if data.name is not None:
            res.name = data.name
        if data.resource_type is not None:
            res.resource_type = data.resource_type
        if data.location is not None:
            res.location = data.location
        if data.capacity is not None:
            res.capacity = data.capacity
        if data.operating_start is not None:
            res.operating_start = data.operating_start
        if data.operating_end is not None:
            res.operating_end = data.operating_end
        if data.status is not None:
            res.status = data.status
        if data.maintenance_start is not None:
            res.maintenance_start = data.maintenance_start
        if data.maintenance_end is not None:
            res.maintenance_end = data.maintenance_end

        if data.equipment is not None:
            db.query(ResourceEquipment).filter(ResourceEquipment.resource_id == res.id).delete()
            for eq in data.equipment:
                db.add(ResourceEquipment(resource_id=res.id, equipment_name=eq))

        db.commit()
        db.refresh(res)
        return res

    @staticmethod
    def delete(db: Session, resource_id: int):
        res = ResourceService.get_by_id(db, resource_id)
        db.delete(res)
        db.commit()

    @staticmethod
    def get_availability(db: Session, resource_id: int, date_str: str) -> ResourceAvailabilityResponse:
        res = ResourceService.get_by_id(db, resource_id)

        # Active confirmed bookings on that day
        bookings = db.query(Booking).filter(
            Booking.resource_id == resource_id,
            Booking.date == date_str,
            Booking.status.in_([BookingStatus.APPROVED, BookingStatus.RESCHEDULED])
        ).order_by(Booking.start_time).all()

        booked_slots = [
            TimeSlot(
                start_time=b.start_time,
                end_time=b.end_time,
                is_available=False,
                booking_id=b.id,
                event_name=b.event_name
            )
            for b in bookings
        ]

        # Calculate free slots between operating hours
        op_s = time_to_minutes(res.operating_start)
        op_e = time_to_minutes(res.operating_end)
        curr = op_s
        available_slots = []

        for b in bookings:
            b_s = time_to_minutes(b.start_time)
            b_e = time_to_minutes(b.end_time)
            if b_s > curr:
                s_str = f"{curr // 60:02d}:{curr % 60:02d}"
                e_str = f"{b_s // 60:02d}:{b_s % 60:02d}"
                available_slots.append(TimeSlot(start_time=s_str, end_time=e_str, is_available=True))
            curr = max(curr, b_e)

        if curr < op_e:
            s_str = f"{curr // 60:02d}:{curr % 60:02d}"
            e_str = f"{op_e // 60:02d}:{op_e % 60:02d}"
            available_slots.append(TimeSlot(start_time=s_str, end_time=e_str, is_available=True))

        is_op = res.status == ResourceStatus.ACTIVE
        maint_reason = None
        if not is_op:
            maint_reason = "Resource is currently marked for maintenance or inactive."

        return ResourceAvailabilityResponse(
            resource_id=res.id,
            resource_name=res.name,
            date=date_str,
            operating_start=res.operating_start,
            operating_end=res.operating_end,
            status=res.status,
            is_operational=is_op,
            maintenance_reason=maint_reason,
            booked_slots=booked_slots,
            available_slots=available_slots
        )
