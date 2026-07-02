from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional

from app.database.session import get_db
from app.models.timetable import Timetable, TimeSlot, RoomAllocation
from app.models.faculty import Faculty, FacultyWorkload
from app.models.room import Classroom, Laboratory
from app.models.subject import Course

router = APIRouter()

@router.get("/workload")
def get_faculty_workload_report(
    academic_year: str = Query("2025-2026"),
    db: Session = Depends(get_db)
):
    """
    Returns teaching workload reports for all faculty members including name, 
    designation, scheduled hours, and percentage load.
    """
    faculty_list = db.query(Faculty).all()
    
    report = []
    designation_limits = {
        "Professor": 12,
        "Associate Professor": 14,
        "Assistant Professor": 16,
        "Lecturer": 18
    }
    
    for f in faculty_list:
        max_allowed = designation_limits.get(f.designation, 18)
        
        # Calculate real-time hours scheduled in timetable
        scheduled_hours = db.query(Timetable).filter(
            Timetable.faculty_id == f.faculty_id,
            Timetable.academic_year == academic_year
        ).count()
        
        utilization = round((scheduled_hours / max_allowed) * 100, 1) if max_allowed > 0 else 0
        
        report.append({
            "faculty_id": f.faculty_id,
            "name": f"{f.first_name} {f.last_name}",
            "designation": f.designation,
            "employee_code": f.employee_code,
            "max_hours": max_allowed,
            "scheduled_hours": scheduled_hours,
            "utilization_percentage": min(utilization, 100.0)
        })
        
    return report

@router.get("/utilization")
def get_room_utilization_report(
    academic_year: str = Query("2025-2026"),
    db: Session = Depends(get_db)
):
    """
    Computes occupancy utilization metrics for all classrooms and laboratories.
    Assumes standard capacity of 40 available slots per week (5 days * 8 periods).
    """
    classrooms = db.query(Classroom).filter(Classroom.is_available == True).all()
    laboratories = db.query(Laboratory).filter(Laboratory.is_available == True).all()
    
    total_slots_per_week = 40.0
    report = []
    
    # Process Classrooms
    for c in classrooms:
        booked_count = db.query(RoomAllocation).join(Timetable).filter(
            RoomAllocation.classroom_id == c.classroom_id,
            RoomAllocation.room_type == "Classroom",
            Timetable.academic_year == academic_year
        ).count()
        
        utilization = round((booked_count / total_slots_per_week) * 100, 1)
        
        report.append({
            "room_id": c.classroom_id,
            "room_number": c.room_number,
            "room_type": "Classroom",
            "building": c.building,
            "capacity": c.capacity,
            "booked_slots": booked_count,
            "utilization_percentage": min(utilization, 100.0)
        })
        
    # Process Laboratories
    for l in laboratories:
        booked_count = db.query(RoomAllocation).join(Timetable).filter(
            RoomAllocation.lab_id == l.lab_id,
            RoomAllocation.room_type == "Laboratory",
            Timetable.academic_year == academic_year
        ).count()
        
        utilization = round((booked_count / total_slots_per_week) * 100, 1)
        
        report.append({
            "room_id": l.lab_id,
            "room_number": l.lab_number,
            "room_type": "Laboratory",
            "building": l.building,
            "capacity": l.capacity,
            "booked_slots": booked_count,
            "utilization_percentage": min(utilization, 100.0)
        })
        
    return report

@router.get("/weekly-stats")
def get_weekly_statistics(
    academic_year: str = Query("2025-2026"),
    db: Session = Depends(get_db)
):
    """
    Returns weekly scheduled breakdown analysis of class types (Lectures, Tutorials, Labs).
    """
    total_classes = db.query(Timetable).filter(Timetable.academic_year == academic_year).count()
    
    # Query breakdowns by course type
    type_counts = db.query(
        Course.course_type, 
        func.count(Timetable.timetable_id)
    ).join(Timetable).filter(
        Timetable.academic_year == academic_year
    ).group_by(Course.course_type).all()
    
    breakdown = {"Theory": 0, "Lab": 0, "Tutorial": 0}
    for c_type, count in type_counts:
        if c_type in breakdown:
            breakdown[c_type] = count
            
    return {
        "total_classes": total_classes,
        "breakdown": breakdown
    }

@router.get("/monthly-stats")
def get_monthly_statistics(
    academic_year: str = Query("2025-2026"),
    db: Session = Depends(get_db)
):
    """
    Returns estimated monthly syllabus hours coverage projections.
    Assumes standard 4-week academic month.
    """
    # Sum scheduled hours in timetable
    weekly_hours = db.query(Timetable).filter(Timetable.academic_year == academic_year).count()
    monthly_hours_projected = weekly_hours * 4
    
    return {
        "projected_monthly_contact_hours": monthly_hours_projected,
        "academic_month_weeks": 4,
        "syllabus_coverage_estimate_percentage": 25.0 if weekly_hours > 0 else 0.0
    }
