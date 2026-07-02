import pytest
from app.services.conflict_checker import (
    check_faculty_conflict,
    check_room_conflict,
    check_section_conflict,
    check_weekly_workload_violation,
    check_lab_clash,
    validate_timetable_entry
)
from app.models.timetable import Timetable, RoomAllocation, ConstraintModel

def test_no_conflicts_initially(db_session):
    """
    Ensures that a proposed assignment on an empty schedule resolves with zero conflicts.
    """
    conflicts = validate_timetable_entry(
        db=db_session,
        section_id=1,
        course_id=1,
        faculty_id=1,
        slot_id=1,
        room_id=1,
        room_type="Classroom",
        academic_year="2025-2026"
    )
    assert len(conflicts) == 0

def test_faculty_double_booking_conflict(db_session):
    """
    Verifies that a faculty conflict is detected if the teacher is assigned 
    to two classes in the same slot.
    """
    # 1. Create a prior booking for Faculty 1 in Slot 1
    tb1 = Timetable(
        section_id=1,
        course_id=1,
        faculty_id=1,
        slot_id=1,
        academic_year="2025-2026",
        semester=3
    )
    db_session.add(tb1)
    db_session.commit()
    
    # 2. Propose another booking for Faculty 1 in Slot 1 (different section, say Section 2)
    conflict = check_faculty_conflict(
        db=db_session,
        faculty_id=1,
        slot_id=1,
        academic_year="2025-2026"
    )
    assert conflict is not None
    assert conflict["type"] == "Faculty_Conflict"
    assert "already teaching" in conflict["message"]

def test_section_double_booking_conflict(db_session):
    """
    Verifies that a section conflict is detected if a class is proposed 
    for a section that is already occupied.
    """
    tb1 = Timetable(
        section_id=1,
        course_id=1,
        faculty_id=1,
        slot_id=1,
        academic_year="2025-2026",
        semester=3
    )
    db_session.add(tb1)
    db_session.commit()
    
    conflict = check_section_conflict(
        db=db_session,
        section_id=1,
        slot_id=1,
        academic_year="2025-2026"
    )
    assert conflict is not None
    assert conflict["type"] == "Section_Conflict"
    assert "already attending" in conflict["message"]

def test_classroom_double_booking_conflict(db_session):
    """
    Verifies that a room conflict is detected if a room is assigned 
    to two different sections at the same time.
    """
    tb1 = Timetable(
        section_id=1,
        course_id=1,
        faculty_id=1,
        slot_id=1,
        academic_year="2025-2026",
        semester=3
    )
    db_session.add(tb1)
    db_session.commit()
    
    ra1 = RoomAllocation(
        timetable_id=tb1.timetable_id,
        room_type="Classroom",
        classroom_id=1
    )
    db_session.add(ra1)
    db_session.commit()
    
    conflict = check_room_conflict(
        db=db_session,
        room_id=1,
        room_type="Classroom",
        slot_id=1,
        academic_year="2025-2026"
    )
    assert conflict is not None
    assert conflict["type"] == "Room_Conflict"
    assert "already booked" in conflict["message"]

def test_room_unavailability_constraint(db_session):
    """
    Verifies that room unavailability rules are correctly evaluated.
    """
    c = ConstraintModel(
        constraint_type="Room_Unavailability",
        classroom_id=1,
        slot_id=1,
        description="Maintenance check",
        is_active=True
    )
    db_session.add(c)
    db_session.commit()
    
    conflict = check_room_conflict(
        db=db_session,
        room_id=1,
        room_type="Classroom",
        slot_id=1,
        academic_year="2025-2026"
    )
    assert conflict is not None
    assert conflict["type"] == "Room_Unavailability"
    assert "unavailable" in conflict["message"]

def test_capacity_violation(db_session):
    """
    Verifies that room capacity violations are raised if the student 
    strength of a section exceeds room seat availability.
    """
    # Lab 1 capacity is 40 in conftest.py, Section 1 size is 60.
    conflict = check_lab_clash(
        db=db_session,
        course_id=1,
        room_id=1,
        room_type="Laboratory",
        section_id=1
    )
    assert conflict is not None
    assert conflict["type"] == "Capacity_Violation"

def test_room_type_clash(db_session):
    """
    Verifies that a room type clash is raised if a theory course 
    is assigned to a laboratory room.
    """
    # Course 1 is type "Theory" in conftest.py. Let's try assigning it to Laboratory 1
    # We use Section 2 to prevent capacity issues (strength 30)
    from app.models.section import Section
    sec2 = Section(
        section_id=2,
        section_name="CSE-B",
        department_id=1,
        semester=3,
        academic_year="2025-2026",
        student_strength=30
    )
    db_session.add(sec2)
    db_session.commit()
    
    conflict = check_lab_clash(
        db=db_session,
        course_id=1,
        room_id=1,
        room_type="Laboratory",
        section_id=2
    )
    assert conflict is not None
    assert conflict["type"] == "Lab_Clash"
    assert "Laboratory" in conflict["message"]

def test_weekly_workload_hours_violation(db_session):
    """
    Verifies that workload violations are raised if scheduled teaching 
    hours exceed the designation limit (Professor = 12 hours).
    """
    from app.models.timetable import TimeSlot
    from datetime import time
    
    # 1. Add 15 unique slots dynamically (ensuring unique day/time combinations on unseeded days)
    for s_id in range(100, 115):
        hour = (s_id - 100) % 12
        day = "Wednesday" if s_id < 108 else "Thursday"
        slot = TimeSlot(
            slot_id=s_id,
            day_of_week=day,
            start_time=time(hour + 6, 0), # hours from 6am to 6pm
            end_time=time(hour + 7, 0),
            slot_order=s_id
        )
        db_session.add(slot)
    db_session.commit()

    # 2. Create 12 bookings using the unique slot IDs
    for i in range(12):
        tb = Timetable(
            section_id=1,
            course_id=1,
            faculty_id=1,
            slot_id=100 + i,
            academic_year="2025-2026",
            semester=3
        )
        db_session.add(tb)
    db_session.commit()
    
    # Adding 1 more hour should fail
    conflict = check_weekly_workload_violation(
        db=db_session,
        faculty_id=1,
        academic_year="2025-2026",
        semester=3,
        proposed_hours=1
    )
    assert conflict is not None
    assert conflict["type"] == "Weekly_Workload_Violation"
