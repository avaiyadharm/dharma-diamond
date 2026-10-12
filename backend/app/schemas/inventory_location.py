from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LocationBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class LocationOut(LocationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
