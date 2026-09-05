from pydantic import BaseModel
from typing import Optional

class AllocationResponse(BaseModel):
    id: int
    booking_id: int
    resource_id: int
    resource_name: Optional[str] = None
    date: str
    start_time: str
    end_time: str
    status: str

    class Config:
        from_attributes = True
