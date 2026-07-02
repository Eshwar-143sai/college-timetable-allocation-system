from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any, Optional

from app.models.timetable import Timetable, TimeSlot, RoomAllocation, ConstraintModel
from app.models.faculty import Faculty, FacultyWorkload
from app.models.subject import Course, Ltpsc, FacultySubject
from app.models.section import Section
from app.models.room import Classroom, Laboratory

def check_faculty_conflict(
    db: Session, 
    faculty_id: int, 
    slot_id: int, 
    academic_year: str, 
    exclude_timetable_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Checks if the faculty member is already scheduled in another slot or has unavailability.
    """
    # 1. Check double booking
    query = db.query(Timetable).filter(
        Timetable.faculty_id == faculty_id,
        Timetable.slot_id == slot_id,
        Timetable.academic_year == academic_year
    )
    if exclude_timetable_id:
        query = query.filter(Timetable.timetable_id != exclude_timetable_id)
        
    double_booking = query.first()
    if double_booking:
        slot = db.query(TimeSlot).filter(TimeSlot.slot_id == slot_id).first()
        day = slot.day_of_week if slot else "Unknown Day"
        time = f"{slot.start_time} - {slot.end_time}" if slot else "Unknown Time"
        return {
            "type": "Faculty_Conflict",
            "message": f"Faculty member is already teaching course '{double_booking.course.course_name} ({double_booking.course.course_code})' during this slot on {day} ({time})."
        }
        
    # 2. Check unavailability constraint
    unavail = db.query(ConstraintModel).filter(
        ConstraintModel.constraint_type == "Faculty_Unavailability",
        ConstraintModel.faculty_id == faculty_id,
        ConstraintModel.slot_id == slot_id,
        ConstraintModel.is_active == True
    ).first()
    if unavail:
        return {
            "type": "Faculty_Unavailability",
            "message": f"Faculty member is unavailable during this slot. Reason: {unavail.description or 'No reason provided'}."
        }
        
    return None

def check_room_conflict(
    db: Session, 
    room_id: int, 
    room_type: str, 
    slot_id: int, 
    academic_year: str, 
    exclude_timetable_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Checks if the classroom or laboratory is already allocated during the slot or is unavailable.
    """
    # 1. Check room double booking
    query = db.query(RoomAllocation).join(Timetable).filter(
        Timetable.slot_id == slot_id,
        Timetable.academic_year == academic_year,
        RoomAllocation.room_type == room_type
    )
    if room_type == "Classroom":
        query = query.filter(RoomAllocation.classroom_id == room_id)
    else:
        query = query.filter(RoomAllocation.lab_id == room_id)
        
    if exclude_timetable_id:
        query = query.filter(Timetable.timetable_id != exclude_timetable_id)
        
    double_booking = query.first()
    if double_booking:
        slot = db.query(TimeSlot).filter(TimeSlot.slot_id == slot_id).first()
        day = slot.day_of_week if slot else "Unknown Day"
        room_name = double_booking.classroom.room_number if room_type == "Classroom" else double_booking.lab.lab_number
        return {
            "type": "Room_Conflict",
            "message": f"The {room_type} {room_name} is already booked for section '{double_booking.timetable.section.section_name}' during this slot on {day}."
        }
        
    # 2. Check room unavailability constraint
    query_unavail = db.query(ConstraintModel).filter(
        ConstraintModel.constraint_type == "Room_Unavailability",
        ConstraintModel.slot_id == slot_id,
        ConstraintModel.is_active == True
    )
    if room_type == "Classroom":
        query_unavail = query_unavail.filter(ConstraintModel.classroom_id == room_id)
        room_name = db.query(Classroom.room_number).filter(Classroom.classroom_id == room_id).scalar() or f"ID {room_id}"
    else:
        query_unavail = query_unavail.filter(ConstraintModel.lab_id == room_id)
        room_name = db.query(Laboratory.lab_number).filter(Laboratory.lab_id == room_id).scalar() or f"ID {room_id}"
        
    unavail = query_unavail.first()
    if unavail:
        return {
            "type": "Room_Unavailability",
            "message": f"The {room_type} {room_name} is marked as unavailable during this slot. Reason: {unavail.description or 'No reason provided'}."
        }
        
    return None

def check_section_conflict(
    db: Session, 
    section_id: int, 
    slot_id: int, 
    academic_year: str, 
    exclude_timetable_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Checks if the section is already scheduled for another course during this slot.
    """
    query = db.query(Timetable).filter(
        Timetable.section_id == section_id,
        Timetable.slot_id == slot_id,
        Timetable.academic_year == academic_year
    )
    if exclude_timetable_id:
        query = query.filter(Timetable.timetable_id != exclude_timetable_id)
        
    double_booking = query.first()
    if double_booking:
        slot = db.query(TimeSlot).filter(TimeSlot.slot_id == slot_id).first()
        day = slot.day_of_week if slot else "Unknown Day"
        return {
            "type": "Section_Conflict",
            "message": f"Section '{double_booking.section.section_name}' is already attending '{double_booking.course.course_code} - {double_booking.course.course_name}' during this slot on {day}."
        }
        
    return None

def check_daily_workload_violation(
    db: Session, 
    faculty_id: int, 
    slot_id: int, 
    academic_year: str, 
    exclude_timetable_id: Optional[int] = None,
    max_hours_per_day: int = 6
) -> Optional[Dict[str, Any]]:
    """
    Ensures a faculty member is not scheduled for more than max_hours_per_day on the target day.
    """
    target_slot = db.query(TimeSlot).filter(TimeSlot.slot_id == slot_id).first()
    if not target_slot:
        return None
        
    # Get all bookings of this faculty on the same day of the week
    bookings = db.query(Timetable).join(TimeSlot).filter(
        Timetable.faculty_id == faculty_id,
        TimeSlot.day_of_week == target_slot.day_of_week,
        Timetable.academic_year == academic_year
    )
    if exclude_timetable_id:
        bookings = bookings.filter(Timetable.timetable_id != exclude_timetable_id)
        
    count = bookings.count()
    if count >= max_hours_per_day:
        return {
            "type": "Daily_Workload_Violation",
            "message": f"Faculty member daily teaching workload limit of {max_hours_per_day} hours exceeded on {target_slot.day_of_week} (currently scheduled for {count} hours)."
        }
        
    return None

def check_weekly_workload_violation(
    db: Session, 
    faculty_id: int, 
    academic_year: str, 
    semester: int, 
    proposed_hours: int = 1,
    exclude_timetable_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Ensures faculty member does not exceed their weekly workload hours allowed.
    """
    # Get designation mapping
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        return None
        
    # Determine max hours limits
    designation_limits = {
        "Professor": 12,
        "Associate Professor": 14,
        "Assistant Professor": 16,
        "Lecturer": 18
    }
    max_allowed = designation_limits.get(faculty.designation, 18)
    
    # Calculate current hours directly from timetable to ensure real-time accuracy
    query = db.query(Timetable).filter(
        Timetable.faculty_id == faculty_id,
        Timetable.academic_year == academic_year,
        Timetable.semester == semester
    )
    if exclude_timetable_id:
        query = query.filter(Timetable.timetable_id != exclude_timetable_id)
        
    # In this simplified model, each timetable row represents a single 1-hour slot
    # (except labs, but they are also entered as separate slots).
    current_hours = query.count()
    
    if current_hours + proposed_hours > max_allowed:
        return {
            "type": "Weekly_Workload_Violation",
            "message": f"Weekly workload violation for {faculty.first_name} {faculty.last_name}: "
                       f"Adding this session would require {current_hours + proposed_hours} hours per week, "
                       f"exceeding the limit of {max_allowed} hours allowed for a {faculty.designation}."
        }
        
    return None

def check_lab_clash(
    db: Session, 
    course_id: int, 
    room_id: int, 
    room_type: str, 
    section_id: int
) -> Optional[Dict[str, Any]]:
    """
    Validates room type matching (Lab course requires Laboratory, Theory requires Classroom) 
    and verifies capacity.
    """
    course = db.query(Course).filter(Course.course_id == course_id).first()
    section = db.query(Section).filter(Section.section_id == section_id).first()
    if not course or not section:
        return None
        
    # 1. Capacity check
    if room_type == "Classroom":
        room = db.query(Classroom).filter(Classroom.classroom_id == room_id).first()
        room_name = room.room_number if room else f"ID {room_id}"
        capacity = room.capacity if room else 0
    else:
        room = db.query(Laboratory).filter(Laboratory.lab_id == room_id).first()
        room_name = room.lab_number if room else f"ID {room_id}"
        capacity = room.capacity if room else 0
        
    if section.student_strength > capacity:
        return {
            "type": "Capacity_Violation",
            "message": f"Section strength ({section.student_strength} students) exceeds the capacity of {room_type} {room_name} ({capacity} seats)."
        }
        
    # 2. Type matching checks
    if course.course_type == "Lab" and room_type != "Laboratory":
        return {
            "type": "Lab_Clash",
            "message": f"Practical/Lab course '{course.course_name}' must be scheduled in a Laboratory, not a Classroom."
        }
        
    if course.course_type == "Theory" and room_type != "Classroom":
        return {
            "type": "Lab_Clash",
            "message": f"Theory course '{course.course_name}' must be scheduled in a Classroom, not a Laboratory."
        }
        
    return None

def check_credit_violation(
    db: Session, 
    section_id: int, 
    course_id: int, 
    academic_year: str, 
    proposed_hours: int = 1,
    exclude_timetable_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Ensures that scheduling hours in the timetable does not exceed L-T-P contact hours limit for a course.
    """
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course or not course.ltpsc:
        return None
        
    ltpsc = course.ltpsc
    total_contact_hours = int(ltpsc.lecture_hours + ltpsc.tutorial_hours + ltpsc.practical_hours)
    
    # Query current scheduled hours for this section and course
    query = db.query(Timetable).filter(
        Timetable.section_id == section_id,
        Timetable.course_id == course_id,
        Timetable.academic_year == academic_year
    )
    if exclude_timetable_id:
        query = query.filter(Timetable.timetable_id != exclude_timetable_id)
        
    current_scheduled = query.count()
    
    if current_scheduled + proposed_hours > total_contact_hours:
        return {
            "type": "Credit_Violation",
            "message": f"Weekly contact hours limit of {total_contact_hours} hours (L={ltpsc.lecture_hours}, T={ltpsc.tutorial_hours}, P={ltpsc.practical_hours}) "
                       f"exceeded for Course '{course.course_name}' in Section '{section_id}'. "
                       f"Proposed assignment would schedule {current_scheduled + proposed_hours} hours."
        }
        
    return None

def validate_timetable_entry(
    db: Session, 
    section_id: int, 
    course_id: int, 
    faculty_id: int, 
    slot_id: int, 
    room_id: int, 
    room_type: str, 
    academic_year: str, 
    current_timetable_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Runs all conflict checks for a proposed timetable assignment.
    
    Returns:
        List[Dict[str, Any]]: A list of detected conflicts. Empty list means the assignment is clean.
    """
    conflicts = []
    
    # 1. Faculty checks
    fac_conf = check_faculty_conflict(db, faculty_id, slot_id, academic_year, current_timetable_id)
    if fac_conf:
        conflicts.append(fac_conf)
        
    # 2. Room checks
    room_conf = check_room_conflict(db, room_id, room_type, slot_id, academic_year, current_timetable_id)
    if room_conf:
        conflicts.append(room_conf)
        
    # 3. Section checks
    sec_conf = check_section_conflict(db, section_id, slot_id, academic_year, current_timetable_id)
    if sec_conf:
        conflicts.append(sec_conf)
        
    # 4. Daily workload checks
    daily_workload = check_daily_workload_violation(db, faculty_id, slot_id, academic_year, current_timetable_id)
    if daily_workload:
        conflicts.append(daily_workload)
        
    # 5. Course and Sem details for weekly workloads
    course = db.query(Course).filter(Course.course_id == course_id).first()
    semester = course.semester if course else 1
    
    # 6. Weekly workload checks
    weekly_workload = check_weekly_workload_violation(db, faculty_id, academic_year, semester, 1, current_timetable_id)
    if weekly_workload:
        conflicts.append(weekly_workload)
        
    # 7. Lab and Capacity clash checks
    lab_conf = check_lab_clash(db, course_id, room_id, room_type, section_id)
    if lab_conf:
        conflicts.append(lab_conf)
        
    # 8. Credit/Hours limit checks
    credit_conf = check_credit_violation(db, section_id, course_id, academic_year, 1, current_timetable_id)
    if credit_conf:
        conflicts.append(credit_conf)
        
    return conflicts
