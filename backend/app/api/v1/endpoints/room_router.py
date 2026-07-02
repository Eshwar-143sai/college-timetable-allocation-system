from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.database.session import get_db
from app.models.room import Classroom, Laboratory
from app.schemas.room_schema import (
    ClassroomCreate, ClassroomUpdate, ClassroomResponse,
    LaboratoryCreate, LaboratoryUpdate, LaboratoryResponse
)

router = APIRouter()

# ==========================================
# CLASSROOMS ENDPOINTS
# ==========================================

@router.get("/classrooms", response_model=List[ClassroomResponse])
def list_classrooms(
    building: Optional[str] = Query(None, description="Filter by building"),
    available_only: Optional[bool] = Query(None, description="Filter by availability"),
    db: Session = Depends(get_db)
):
    query = db.query(Classroom)
    if building:
        query = query.filter(Classroom.building == building)
    if available_only is not None:
        query = query.filter(Classroom.is_available == available_only)
    return query.all()

@router.get("/classrooms/{classroom_id}", response_model=ClassroomResponse)
def get_classroom(classroom_id: int, db: Session = Depends(get_db)):
    room = db.query(Classroom).filter(Classroom.classroom_id == classroom_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    return room

@router.post("/classrooms", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
def create_classroom(room_in: ClassroomCreate, db: Session = Depends(get_db)):
    # Check uniqueness
    existing = db.query(Classroom).filter(Classroom.room_number == room_in.room_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Classroom with room number {room_in.room_number} already exists"
        )
        
    room = Classroom(**room_in.dict())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@router.put("/classrooms/{classroom_id}", response_model=ClassroomResponse)
def update_classroom(classroom_id: int, room_in: ClassroomUpdate, db: Session = Depends(get_db)):
    room = db.query(Classroom).filter(Classroom.classroom_id == classroom_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
        
    # Check uniqueness if room number is changed
    if room_in.room_number is not None and room_in.room_number != room.room_number:
        existing = db.query(Classroom).filter(Classroom.room_number == room_in.room_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Classroom with room number {room_in.room_number} already exists"
            )
            
    update_data = room_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)
        
    db.commit()
    db.refresh(room)
    return room

@router.delete("/classrooms/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_classroom(classroom_id: int, db: Session = Depends(get_db)):
    room = db.query(Classroom).filter(Classroom.classroom_id == classroom_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    db.delete(room)
    db.commit()
    return None


# ==========================================
# LABORATORIES ENDPOINTS
# ==========================================

@router.get("/laboratories", response_model=List[LaboratoryResponse])
def list_laboratories(
    building: Optional[str] = Query(None, description="Filter by building"),
    available_only: Optional[bool] = Query(None, description="Filter by availability"),
    db: Session = Depends(get_db)
):
    query = db.query(Laboratory)
    if building:
        query = query.filter(Laboratory.building == building)
    if available_only is not None:
        query = query.filter(Laboratory.is_available == available_only)
    return query.all()

@router.get("/laboratories/{lab_id}", response_model=LaboratoryResponse)
def get_laboratory(lab_id: int, db: Session = Depends(get_db)):
    lab = db.query(Laboratory).filter(Laboratory.lab_id == lab_id).first()
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratory not found"
        )
    return lab

@router.post("/laboratories", response_model=LaboratoryResponse, status_code=status.HTTP_201_CREATED)
def create_laboratory(lab_in: LaboratoryCreate, db: Session = Depends(get_db)):
    # Check uniqueness
    existing = db.query(Laboratory).filter(Laboratory.lab_number == lab_in.lab_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Laboratory with lab number {lab_in.lab_number} already exists"
        )
        
    lab = Laboratory(**lab_in.dict())
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab

@router.put("/laboratories/{lab_id}", response_model=LaboratoryResponse)
def update_laboratory(lab_id: int, lab_in: LaboratoryUpdate, db: Session = Depends(get_db)):
    lab = db.query(Laboratory).filter(Laboratory.lab_id == lab_id).first()
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratory not found"
        )
        
    # Check uniqueness if lab number is changed
    if lab_in.lab_number is not None and lab_in.lab_number != lab.lab_number:
        existing = db.query(Laboratory).filter(Laboratory.lab_number == lab_in.lab_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Laboratory with lab number {lab_in.lab_number} already exists"
            )
            
    update_data = lab_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lab, field, value)
        
    db.commit()
    db.refresh(lab)
    return lab

@router.delete("/laboratories/{lab_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_laboratory(lab_id: int, db: Session = Depends(get_db)):
    lab = db.query(Laboratory).filter(Laboratory.lab_id == lab_id).first()
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratory not found"
        )
    db.delete(lab)
    db.commit()
    return None
