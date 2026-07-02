import pytest
from app.scheduler.constraint_solver import TimetableScheduler
from app.models.timetable import Timetable, RoomAllocation, TimeSlot
from app.models.faculty import FacultyWorkload

def test_scheduler_solves_successfully(db_session):
    """
    Integration test asserting that the scheduling engine successfully allocates 
    all sessions without conflicts and persists allocations.
    """
    # 1. Initialize scheduler for 2025-2026
    scheduler = TimetableScheduler(db_session, "2025-2026")
    
    # 2. Run solver
    success = scheduler.solve()
    
    # Assert solver succeeded
    assert success is True
    assert len(scheduler.assignments) > 0
    
    # 3. Save timetable allocations to database
    scheduler.save_timetable()
    
    # 4. Query database to verify rows were persisted
    timetables = db_session.query(Timetable).all()
    assert len(timetables) > 0
    
    # Verify room allocations exist
    allocations = db_session.query(RoomAllocation).all()
    assert len(allocations) == len(timetables)
    
    # Verify workloads exist
    workloads = db_session.query(FacultyWorkload).all()
    assert len(workloads) > 0
    
    # Check details of first booking
    first_booking = timetables[0]
    assert first_booking.academic_year == "2025-2026"
    assert first_booking.section_id == 1
    assert first_booking.course_id == 1
    assert first_booking.faculty_id == 1
    
    # Confirm room allocation detail
    ra = db_session.query(RoomAllocation).filter(RoomAllocation.timetable_id == first_booking.timetable_id).first()
    assert ra is not None
    assert ra.room_type == "Classroom"
    assert ra.classroom_id == 1
