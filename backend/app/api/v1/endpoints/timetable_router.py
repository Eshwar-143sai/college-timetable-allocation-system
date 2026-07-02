from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.timetable import Timetable, TimeSlot, RoomAllocation
from app.models.section import Section
from app.models.subject import Course
from app.models.faculty import Faculty
from app.scheduler.constraint_solver import TimetableScheduler
from app.services.conflict_checker import validate_timetable_entry
from app.schemas.timetable_schema import TimetableValidationRequest, TimetableValidationResponse

router = APIRouter()

@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_timetable(
    academic_year: str = Query("2025-2026", description="Academic year to generate schedule for"),
    db: Session = Depends(get_db)
):
    """
    Triggers the CSP solver algorithm to dynamically allocate all courses, faculty, and rooms 
    into time slots without conflicts.
    """
    try:
        scheduler = TimetableScheduler(db, academic_year)
        success = scheduler.solve()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Timetable scheduling failed: Constraints are unsatisfiable. Please add rooms or allocate more faculty."
            )
            
        scheduler.save_timetable()
        return {"message": f"Timetable generated and saved successfully for academic year {academic_year}!"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scheduling engine error: {str(e)}"
        )

@router.get("/")
def get_timetable(
    section_id: Optional[int] = Query(None, description="Filter by section"),
    faculty_id: Optional[int] = Query(None, description="Filter by faculty member"),
    classroom_id: Optional[int] = Query(None, description="Filter by classroom"),
    lab_id: Optional[int] = Query(None, description="Filter by laboratory"),
    academic_year: str = Query("2025-2026"),
    db: Session = Depends(get_db)
):
    """
    Retrieves the generated schedule with options to filter by Section, Faculty, or Room.
    """
    query = db.query(Timetable).filter(Timetable.academic_year == academic_year)
    
    if section_id:
        query = query.filter(Timetable.section_id == section_id)
    if faculty_id:
        query = query.filter(Timetable.faculty_id == faculty_id)
        
    results = query.all()
    
    # Resolve room details for each entry
    timetable_list = []
    for item in results:
        # Get room allocation
        ra = item.room_allocation
        room_details = None
        if ra:
            if ra.room_type == "Classroom" and ra.classroom:
                room_details = {
                    "room_type": "Classroom",
                    "room_id": ra.classroom_id,
                    "room_number": ra.classroom.room_number,
                    "building": ra.classroom.building
                }
            elif ra.room_type == "Laboratory" and ra.lab:
                room_details = {
                    "room_type": "Laboratory",
                    "room_id": ra.lab_id,
                    "room_number": ra.lab.lab_number,
                    "building": ra.lab.building
                }
                
        timetable_list.append({
            "timetable_id": item.timetable_id,
            "section_id": item.section_id,
            "section_name": item.section.section_name,
            "course_id": item.course_id,
            "course_code": item.course.course_code,
            "course_name": item.course.course_name,
            "faculty_id": item.faculty_id,
            "faculty_name": f"{item.faculty.first_name} {item.faculty.last_name}",
            "slot_id": item.slot_id,
            "day_of_week": item.slot.day_of_week,
            "start_time": str(item.slot.start_time),
            "end_time": str(item.slot.end_time),
            "slot_order": item.slot.slot_order,
            "room": room_details
        })
        
    return timetable_list

@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_timetable(
    academic_year: str = Query("2025-2026"),
    db: Session = Depends(get_db)
):
    """
    Clears all allocations and timetable records for the academic year.
    """
    db.query(Timetable).filter(Timetable.academic_year == academic_year).delete()
    db.commit()
    return None

@router.post("/validate-entry", response_model=TimetableValidationResponse)
def validate_proposed_entry(
    payload: TimetableValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validates a proposed schedule entry to detect conflicts (Faculty, Room, Section, Workloads, Labs, and Credits) 
    before committing changes.
    """
    conflicts = validate_timetable_entry(
        db=db,
        section_id=payload.section_id,
        course_id=payload.course_id,
        faculty_id=payload.faculty_id,
        slot_id=payload.slot_id,
        room_id=payload.room_id,
        room_type=payload.room_type,
        academic_year=payload.academic_year,
        current_timetable_id=payload.current_timetable_id
    )
    
    is_valid = len(conflicts) == 0
    return {
        "is_valid": is_valid,
        "conflicts": conflicts
    }
