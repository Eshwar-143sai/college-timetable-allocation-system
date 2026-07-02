"""
College Timetable Allocation System — Scheduling Engine
Algorithm: Constraint Satisfaction Problem (CSP) with Backtracking, 
           Priority Queue (Most Constrained Variable First), 
           and Greedy Workload Balancing.

Time Complexity:
    Worst Case: O(F * (S * R)^V)
        - V: Number of variables (sessions to schedule)
        - F: Number of faculty candidates per course
        - S: Number of time slots available
        - R: Number of candidate rooms
    But pruned extremely fast due to:
        - "Labs First" heuristic (P scheduled before L/T)
        - Classroom capacity & type pruning
        - Faculty subject constraints
        - Workload limits pruning
    Average Case: O(V * S * R) in practice (often runs in < 1 second).

Space Complexity:
    O(V + S * (Sec + Fac + R))
        - V: Variable list and call stack depth
        - S: Bookings maps for Sections (Sec), Faculty (Fac), and Rooms (R).
    This is O(N) linear space with respect to the input size, fitting easily in memory.
"""

import heapq
from typing import List, Dict, Tuple, Set, Optional, Any
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.faculty import Faculty, FacultyWorkload
from app.models.subject import Course, Ltpsc, FacultySubject
from app.models.section import Section
from app.models.room import Classroom, Laboratory
from app.models.timetable import TimeSlot, Timetable, RoomAllocation, ConstraintModel

class TimetableScheduler:
    """
    Classroom and Lab Timetable Scheduler Engine.
    Solves the Constraint Satisfaction Problem (CSP) for scheduling university courses.
    """
    
    def __init__(self, db: Session, academic_year: str):
        """
        Initializes the scheduler state by loading all necessary data from the database.
        
        Args:
            db (Session): SQLAlchemy database session.
            academic_year (str): Target academic year (e.g. '2025-2026').
        """
        self.db = db
        self.academic_year = academic_year
        
        # 1. Fetch all reference data from DB
        self.sections = db.query(Section).filter(Section.academic_year == academic_year).all()
        self.faculties = db.query(Faculty).all()
        self.courses = db.query(Course).filter(Course.is_active == True).all()
        self.classrooms = db.query(Classroom).filter(Classroom.is_available == True).all()
        self.laboratories = db.query(Laboratory).filter(Laboratory.is_available == True).all()
        self.slots = db.query(TimeSlot).all()
        self.constraints = db.query(ConstraintModel).filter(ConstraintModel.is_active == True).all()
        
        # 2. Pre-process Time Slots into consecutive lists by day
        self.slots_by_day = self._group_slots_by_day()
        
        # 3. Load constraints into quick-lookup sets
        self.faculty_unavail, self.room_unavail = self._load_constraints()
        
        # 4. Initialize scheduling state maps
        self.section_bookings: Set[Tuple[int, int]] = set()  # (section_id, slot_id)
        self.faculty_bookings: Set[Tuple[int, int]] = set()  # (faculty_id, slot_id)
        self.room_bookings: Set[Tuple[int, str, int]] = set() # (room_id, 'Classroom'|'Laboratory', slot_id)
        
        # Workload trackers
        self.faculty_workloads: Dict[Tuple[int, int], int] = {}  # (faculty_id, semester) -> hours_assigned
        self.faculty_max_hours: Dict[int, int] = {f.faculty_id: f.max_hours_per_week for f in self.faculties}
        
        # Final output storage
        self.assignments: List[Dict[str, Any]] = []

    def _group_slots_by_day(self) -> Dict[str, List[TimeSlot]]:
        """
        Groups time slots by day of the week and sorts them by slot order.
        Essential for finding consecutive slots for Lab sessions.
        
        Returns:
            Dict[str, List[TimeSlot]]: Day mapping to sorted slots.
        """
        grouped = {}
        for slot in self.slots:
            grouped.setdefault(slot.day_of_week, []).append(slot)
            
        for day in grouped:
            grouped[day].sort(key=lambda s: s.slot_order)
        return grouped

    def _load_constraints(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, str, int]]]:
        """
        Loads unavailability constraints into sets for O(1) constant-time conflict checks.
        
        Returns:
            Tuple[Set, Set]: Faculty unavailability (faculty_id, slot_id) and
                             Room unavailability (room_id, room_type, slot_id).
        """
        fac_set = set()
        room_set = set()
        
        for c in self.constraints:
            if c.constraint_type == "Faculty_Unavailability" and c.faculty_id and c.slot_id:
                fac_set.add((c.faculty_id, c.slot_id))
            elif c.constraint_type == "Room_Unavailability" and c.slot_id:
                if c.classroom_id:
                    room_set.add((c.classroom_id, "Classroom", c.slot_id))
                elif c.lab_id:
                    room_set.add((c.lab_id, "Laboratory", c.slot_id))
                    
        return fac_set, room_set

    def _build_variables_queue(self) -> List[Tuple[int, int, int, str, int]]:
        """
        Builds the priority queue of variables to schedule.
        Heuristics used:
            - Labs First (P prioritised over T, which is prioritised over L)
            - Most Constrained Variable (larger sections with higher student strength scheduled first)
        
        Returns:
            List[Tuple]: List of variables sorted by priority.
        """
        variables = []
        
        for sec in self.sections:
            # Find courses matching section's semester and department
            matching_courses = [
                c for c in self.courses 
                if c.semester == sec.semester and c.department_id == sec.department_id
            ]
            
            for course in matching_courses:
                ltpsc = course.ltpsc
                if not ltpsc:
                    continue
                
                # 1. Labs (Practical hours)
                if ltpsc.practical_hours > 0:
                    # Labs are scheduled as a block of practical hours (Priority 1)
                    # Heap item: (Priority, -student_strength, section_id, course_id, type, index, length)
                    heapq.heappush(variables, (
                        1, 
                        -sec.student_strength, 
                        sec.section_id, 
                        course.course_id, 
                        'P', 
                        1, 
                        int(ltpsc.practical_hours)
                    ))
                    
                # 2. Tutorials
                for i in range(1, int(ltpsc.tutorial_hours) + 1):
                    heapq.heappush(variables, (
                        2, 
                        -sec.student_strength, 
                        sec.section_id, 
                        course.course_id, 
                        'T', 
                        i, 
                        1
                    ))
                    
                # 3. Lectures
                for i in range(1, int(ltpsc.lecture_hours) + 1):
                    heapq.heappush(variables, (
                        3, 
                        -sec.student_strength, 
                        sec.section_id, 
                        course.course_id, 
                        'L', 
                        i, 
                        1
                    ))
                    
        # Extract variables from heap to get them sorted by priority
        sorted_vars = []
        while variables:
            item = heapq.heappop(variables)
            # Tuple: (section_id, course_id, session_type, session_index, length)
            sorted_vars.append((item[2], item[3], item[4], item[5], item[6]))
            
        return sorted_vars

    def _get_faculty_candidates(self, course_id: int, semester: int) -> List[int]:
        """
        Retrieves all faculty members assigned to teach a course, sorted by current workload
        to implement Greedy Workload Balancing (load-balancing heuristic).
        
        Args:
            course_id (int): Course identifier.
            semester (int): Current semester.
            
        Returns:
            List[int]: Sorted list of faculty IDs.
        """
        # Fetch faculty subjects
        candidates_raw = self.db.query(FacultySubject.faculty_id).filter(
            FacultySubject.course_id == course_id,
            FacultySubject.academic_year == self.academic_year
        ).all()
        
        candidate_ids = [c[0] for c in candidates_raw]
        
        # Sort candidates by current load ratio (current assigned hours / max allowed hours)
        def get_load_ratio(fac_id: int) -> float:
            assigned = self.faculty_workloads.get((fac_id, semester), 0)
            max_allowed = self.faculty_max_hours.get(fac_id, 18)
            return float(assigned) / max_allowed
            
        candidate_ids.sort(key=get_load_ratio)
        return candidate_ids

    def _find_consecutive_slots(self, day: str, length: int) -> List[List[TimeSlot]]:
        """
        Finds all blocks of consecutive slots of a given length on a specific day.
        
        Args:
            day (str): Day of week.
            length (int): Block length.
            
        Returns:
            List[List[TimeSlot]]: List of consecutive TimeSlot blocks.
        """
        day_slots = self.slots_by_day.get(day, [])
        if len(day_slots) < length:
            return []
            
        blocks = []
        for i in range(len(day_slots) - length + 1):
            block = day_slots[i:i+length]
            
            # Verify slots are indeed consecutive by checking slot order numbers
            is_consecutive = True
            for j in range(len(block) - 1):
                if block[j+1].slot_order != block[j].slot_order + 1:
                    is_consecutive = False
                    break
                    
            if is_consecutive:
                blocks.append(block)
        return blocks

    def _check_conflicts(
        self, 
        section_id: int, 
        faculty_id: int, 
        room_id: int, 
        room_type: str, 
        slots: List[TimeSlot]
    ) -> bool:
        """
        Checks for scheduling conflicts across Section, Faculty, Room booking, 
        and Faculty Unavailability constraints.
        
        Args:
            section_id (int): Section.
            faculty_id (int): Faculty.
            room_id (int): Room or Lab.
            room_type (str): 'Classroom' or 'Laboratory'.
            slots (List[TimeSlot]): List of slots.
            
        Returns:
            bool: True if conflict exists, False if all clear.
        """
        for slot in slots:
            slot_id = slot.slot_id
            
            # 1. Section Collision Check
            if (section_id, slot_id) in self.section_bookings:
                return True
                
            # 2. Faculty Collision Check (and unavailability check)
            if (faculty_id, slot_id) in self.faculty_bookings:
                return True
            if (faculty_id, slot_id) in self.faculty_unavail:
                return True
                
            # 3. Room Collision Check (and unavailability check)
            if (room_id, room_type, slot_id) in self.room_bookings:
                return True
            if (room_id, room_type, slot_id) in self.room_unavail:
                return True
                
        return False

    def _apply_assignment(
        self, 
        section_id: int, 
        course_id: int, 
        faculty_id: int, 
        room_id: int, 
        room_type: str, 
        slots: List[TimeSlot],
        semester: int
    ):
        """
        Applies temporary booking entries to state trackers.
        """
        for slot in slots:
            slot_id = slot.slot_id
            self.section_bookings.add((section_id, slot_id))
            self.faculty_bookings.add((faculty_id, slot_id))
            self.room_bookings.add((room_id, room_type, slot_id))
            
        # Update faculty workload tracking
        self.faculty_workloads[(faculty_id, semester)] = \
            self.faculty_workloads.get((faculty_id, semester), 0) + len(slots)

    def _remove_assignment(
        self, 
        section_id: int, 
        faculty_id: int, 
        room_id: int, 
        room_type: str, 
        slots: List[TimeSlot],
        semester: int
    ):
        """
        Removes temporary booking entries from state trackers (backtracking step).
        """
        for slot in slots:
            slot_id = slot.slot_id
            self.section_bookings.discard((section_id, slot_id))
            self.faculty_bookings.discard((faculty_id, slot_id))
            self.room_bookings.discard((room_id, room_type, slot_id))
            
        # Update faculty workload tracking
        self.faculty_workloads[(faculty_id, semester)] = \
            max(0, self.faculty_workloads.get((faculty_id, semester), 0) - len(slots))

    def solve(self) -> bool:
        """
        Triggers the solving algorithm.
        
        Returns:
            bool: True if a conflict-free solution is found, False otherwise.
        """
        # Build priority queue variables list
        variables = self._build_variables_queue()
        if not variables:
            return True  # Nothing to schedule
            
        # Clear previous state
        self.assignments.clear()
        self.section_bookings.clear()
        self.faculty_bookings.clear()
        self.room_bookings.clear()
        self.faculty_workloads.clear()
        
        # Run backtracking search
        return self._backtrack(variables, 0)

    def _backtrack(self, variables: List[Tuple[int, int, str, int, int]], var_index: int) -> bool:
        """
        Recursive backtracking CSP solver function.
        
        Args:
            variables (List): Queue of variables to assign.
            var_index (int): Index of current variable.
            
        Returns:
            bool: True if recursion path completes successfully.
        """
        # Base Case: All variables scheduled!
        if var_index == len(variables):
            return True
            
        # Get current variable properties
        section_id, course_id, session_type, index, length = variables[var_index]
        
        # Retrieve section semester
        section = next(s for s in self.sections if s.section_id == section_id)
        semester = section.semester
        
        # 1. Find candidate faculties and sort by current load (Greedy load balancer)
        fac_candidates = self._get_faculty_candidates(course_id, semester)
        if not fac_candidates:
            # No faculty member assigned to teach this subject
            return False
            
        # 2. Select appropriate room pool
        rooms_pool = []
        room_type = ""
        if session_type == 'P':
            rooms_pool = self.laboratories
            room_type = "Laboratory"
        else:
            rooms_pool = self.classrooms
            room_type = "Classroom"
            
        # Filter rooms by capacity
        valid_rooms = [
            r for r in rooms_pool 
            if r.capacity >= section.student_strength
        ]
        # Sort rooms by capacity ascending (Best Fit Room heuristic)
        valid_rooms.sort(key=lambda r: r.capacity)
        
        # 3. Iterate candidates to find slot-room assignment
        for faculty_id in fac_candidates:
            # Workload Check
            current_hours = self.faculty_workloads.get((faculty_id, semester), 0)
            max_hours = self.faculty_max_hours.get(faculty_id, 18)
            if current_hours + length > max_hours:
                # Assigning this session would overload the teacher, skip candidate
                continue
                
            # Iterate rooms
            for room in valid_rooms:
                room_id = room.classroom_id if room_type == "Classroom" else room.lab_id
                
                # Check slots availability
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
                    # Find candidate slots (consecutive blocks for labs, single slots for lectures)
                    candidate_blocks = self._find_consecutive_slots(day, length)
                    
                    for block in candidate_blocks:
                        # Conflict Check
                        if self._check_conflicts(section_id, faculty_id, room_id, room_type, block):
                            continue
                            
                        # Apply Assignment
                        self._apply_assignment(section_id, course_id, faculty_id, room_id, room_type, block, semester)
                        
                        # Recurse
                        if self._backtrack(variables, var_index + 1):
                            # Record final assignment details
                            for slot in block:
                                self.assignments.append({
                                    "section_id": section_id,
                                    "course_id": course_id,
                                    "faculty_id": faculty_id,
                                    "slot_id": slot.slot_id,
                                    "semester": semester,
                                    "room_type": room_type,
                                    "room_id": room_id
                                })
                            return True
                            
                        # Backtrack
                        self._remove_assignment(section_id, faculty_id, room_id, room_type, block, semester)
                        
        # If no configuration works for this variable, trigger backtrack on call stack
        return False

    def save_timetable(self):
        """
        Saves the resolved timetable and room allocation records to the database.
        Clears previous timetable rows for this academic year first.
        """
        # Delete old timetable for this academic year
        # This will cascade delete room allocations automatically due to foreign keys
        self.db.query(Timetable).filter(Timetable.academic_year == self.academic_year).delete()
        self.db.commit()
        
        # Save new assignments
        for assign in self.assignments:
            tb = Timetable(
                section_id=assign["section_id"],
                course_id=assign["course_id"],
                faculty_id=assign["faculty_id"],
                slot_id=assign["slot_id"],
                academic_year=self.academic_year,
                semester=assign["semester"]
            )
            self.db.add(tb)
            self.db.commit()
            self.db.refresh(tb)
            
            # Save Room Allocation
            ra = RoomAllocation(
                timetable_id=tb.timetable_id,
                room_type=assign["room_type"],
                classroom_id=assign["room_id"] if assign["room_type"] == "Classroom" else None,
                lab_id=assign["room_id"] if assign["room_type"] == "Laboratory" else None
            )
            self.db.add(ra)
            
        self.db.commit()
        
        # Update faculty workloads in database
        for (fac_id, sem), hours in self.faculty_workloads.items():
            wl = self.db.query(FacultyWorkload).filter(
                FacultyWorkload.faculty_id == fac_id,
                FacultyWorkload.academic_year == self.academic_year,
                FacultyWorkload.semester == sem
            ).first()
            
            max_allowed = self.faculty_max_hours.get(fac_id, 18)
            if wl:
                wl.total_hours_assigned = hours
                wl.max_hours_allowed = max_allowed
            else:
                wl = FacultyWorkload(
                    faculty_id=fac_id,
                    academic_year=self.academic_year,
                    semester=sem,
                    total_hours_assigned=hours,
                    max_hours_allowed=max_allowed
                )
                self.db.add(wl)
                
        self.db.commit()
