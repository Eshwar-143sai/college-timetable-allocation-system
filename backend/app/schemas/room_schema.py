from pydantic import BaseModel, Field
from typing import Optional

# Classroom Schemas
class ClassroomBase(BaseModel):
    room_number: str = Field(..., max_length=20)
    building: str = Field(..., max_length=50)
    floor: int
    capacity: int = Field(..., gt=0)
    has_projector: Optional[bool] = False
    is_available: Optional[bool] = True

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomUpdate(BaseModel):
    room_number: Optional[str] = Field(None, max_length=20)
    building: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = None
    capacity: Optional[int] = Field(None, gt=0)
    has_projector: Optional[bool] = None
    is_available: Optional[bool] = None

class ClassroomResponse(ClassroomBase):
    classroom_id: int

    class Config:
        from_attributes = True

# Laboratory Schemas
class LaboratoryBase(BaseModel):
    lab_number: str = Field(..., max_length=20)
    building: str = Field(..., max_length=50)
    floor: int
    capacity: int = Field(..., gt=0)
    lab_type: str = Field(..., max_length=50)  # e.g., Computer Lab, Electronics Lab
    equipment_details: Optional[str] = None
    is_available: Optional[bool] = True

class LaboratoryCreate(LaboratoryBase):
    pass

class LaboratoryUpdate(BaseModel):
    lab_number: Optional[str] = Field(None, max_length=20)
    building: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = None
    capacity: Optional[int] = Field(None, gt=0)
    lab_type: Optional[str] = Field(None, max_length=50)
    equipment_details: Optional[str] = None
    is_available: Optional[bool] = None

class LaboratoryResponse(LaboratoryBase):
    lab_id: int

    class Config:
        from_attributes = True
