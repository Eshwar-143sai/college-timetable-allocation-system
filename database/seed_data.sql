-- =====================================================================
-- College Time Table Allocation System — Sample / Seed Data
-- Run AFTER schema.sql
-- =====================================================================

USE timetable_db;

-- ---------------------------------------------------------------------
-- 1. DEPARTMENTS
-- ---------------------------------------------------------------------
INSERT INTO departments (department_code, department_name) VALUES
('CSE', 'Computer Science and Engineering'),
('ECE', 'Electronics and Communication Engineering'),
('MECH', 'Mechanical Engineering'),
('CIVIL', 'Civil Engineering');

-- ---------------------------------------------------------------------
-- 2. USERS  (admin, hod, faculty logins, student logins)
-- ---------------------------------------------------------------------
INSERT INTO users (username, email, password_hash, role) VALUES
('admin1',        'admin@college.edu',          '$2b$12$hashvalueadmin000000000000000000000000000000',    'admin'),
('hod_cse',       'hod.cse@college.edu',        '$2b$12$hashvaluehod0000000000000000000000000000000',    'hod'),
('rshah_cse',     'r.shah@college.edu',         '$2b$12$hashvaluefac10000000000000000000000000000000',   'faculty'),
('apatel_cse',    'a.patel@college.edu',        '$2b$12$hashvaluefac20000000000000000000000000000000',   'faculty'),
('skumar_ece',    's.kumar@college.edu',        '$2b$12$hashvaluefac30000000000000000000000000000000',   'faculty'),
('mverma_cse',    'm.verma@college.edu',        '$2b$12$hashvaluefac40000000000000000000000000000000',   'faculty'),
('stud_101',      'ananya.rao@college.edu',     '$2b$12$hashvaluestu10000000000000000000000000000000',   'student'),
('stud_102',      'rahul.nair@college.edu',     '$2b$12$hashvaluestu20000000000000000000000000000000',   'student'),
('stud_103',      'priya.singh@college.edu',    '$2b$12$hashvaluestu30000000000000000000000000000000',   'student');

-- ---------------------------------------------------------------------
-- 3. FACULTY
-- ---------------------------------------------------------------------
INSERT INTO faculty (user_id, employee_code, first_name, last_name, department_id, designation, max_hours_per_week, phone) VALUES
(3, 'EMP1001', 'Rohan',  'Shah',  1, 'Associate Professor', 18, '9876543210'),
(4, 'EMP1002', 'Aditi',  'Patel', 1, 'Assistant Professor', 20, '9876543211'),
(5, 'EMP1003', 'Sanjay', 'Kumar', 2, 'Professor',           16, '9876543212'),
(6, 'EMP1004', 'Meera',  'Verma', 1, 'Lecturer',            22, '9876543213');

-- ---------------------------------------------------------------------
-- 4. LTPSC  (standard curriculum patterns)
-- ---------------------------------------------------------------------
INSERT INTO ltpsc (lecture_hours, tutorial_hours, practical_hours, self_study_hours, credits) VALUES
(3, 0, 0, 0, 3.0),   -- ltpsc_id 1: standard theory course
(3, 1, 0, 0, 4.0),   -- ltpsc_id 2: theory + tutorial
(2, 0, 2, 0, 3.0),   -- ltpsc_id 3: theory + lab combined
(0, 0, 3, 0, 1.5),   -- ltpsc_id 4: standalone lab
(4, 0, 0, 1, 4.5);   -- ltpsc_id 5: heavy theory + self-study

-- ---------------------------------------------------------------------
-- 5. COURSES
-- ---------------------------------------------------------------------
INSERT INTO courses (course_code, course_name, department_id, ltpsc_id, course_type, semester) VALUES
('CS301', 'Database Management Systems',        1, 2, 'Theory',      3),
('CS302', 'Operating Systems',                  1, 1, 'Theory',      3),
('CS303', 'Database Management Systems Lab',    1, 4, 'Lab',         3),
('CS304', 'Web Technologies',                   1, 3, 'Theory+Lab',  3),
('EC201', 'Digital Electronics',                2, 1, 'Theory',      2),
('CS401', 'Machine Learning',                   1, 5, 'Theory',      4);

-- ---------------------------------------------------------------------
-- 6. FACULTY_SUBJECT  (who teaches what, this academic year)
-- ---------------------------------------------------------------------
INSERT INTO faculty_subject (faculty_id, course_id, academic_year) VALUES
(1, 1, '2025-2026'),  -- Rohan Shah -> DBMS
(1, 3, '2025-2026'),  -- Rohan Shah -> DBMS Lab
(2, 2, '2025-2026'),  -- Aditi Patel -> OS
(2, 4, '2025-2026'),  -- Aditi Patel -> Web Tech
(3, 5, '2025-2026'),  -- Sanjay Kumar -> Digital Electronics
(4, 6, '2025-2026');  -- Meera Verma -> Machine Learning

-- ---------------------------------------------------------------------
-- 7. SECTIONS
-- ---------------------------------------------------------------------
INSERT INTO sections (section_name, department_id, semester, academic_year, student_strength) VALUES
('CSE-A', 1, 3, '2025-2026', 60),
('CSE-B', 1, 3, '2025-2026', 58),
('ECE-A', 2, 2, '2025-2026', 55);

-- ---------------------------------------------------------------------
-- 8. STUDENTS
-- ---------------------------------------------------------------------
INSERT INTO students (user_id, roll_number, first_name, last_name, section_id, department_id, admission_year) VALUES
(7, 'CSE2023001', 'Ananya', 'Rao',   1, 1, 2023),
(8, 'CSE2023002', 'Rahul',  'Nair',  1, 1, 2023),
(9, 'CSE2023045', 'Priya',  'Singh', 2, 1, 2023);

-- ---------------------------------------------------------------------
-- 9. CLASSROOMS
-- ---------------------------------------------------------------------
INSERT INTO classrooms (room_number, building, floor, capacity, has_projector, is_available) VALUES
('A-101', 'Block A', 1, 70, TRUE, TRUE),
('A-102', 'Block A', 1, 65, TRUE, TRUE),
('A-201', 'Block A', 2, 70, TRUE, TRUE),
('A-202', 'Block A', 2, 65, FALSE, TRUE),
('B-101', 'Block B', 1, 60, TRUE, TRUE),
('B-102', 'Block B', 1, 60, FALSE, TRUE),
('B-201', 'Block B', 2, 60, FALSE, TRUE),
('B-202', 'Block B', 2, 55, TRUE, TRUE);

-- ---------------------------------------------------------------------
-- 10. LABORATORIES
-- ---------------------------------------------------------------------
INSERT INTO laboratories (lab_number, building, floor, capacity, lab_type, equipment_details, is_available) VALUES
('L-301', 'Block C', 3, 40, 'Computer Lab',    '40 workstations, Ubuntu 24.04, MySQL 8.0 pre-installed', TRUE),
('L-302', 'Block C', 3, 35, 'Electronics Lab', 'Oscilloscopes, function generators, breadboards', TRUE),
('L-401', 'Block C', 4, 40, 'Mechanical Lab',  'CNC machines, lathe machines, drilling equipment', TRUE),
('L-402', 'Block C', 4, 30, 'Physics/Chemistry Lab', 'Chemical safety hoods, spectrometers, optical benches', TRUE);

-- ---------------------------------------------------------------------
-- 11. TIME_SLOTS  (Mon-Fri, 4 periods/day for brevity)
-- ---------------------------------------------------------------------
INSERT INTO time_slots (day_of_week, start_time, end_time, slot_order) VALUES
('Monday',    '09:00:00', '10:00:00', 1),
('Monday',    '10:00:00', '11:00:00', 2),
('Monday',    '11:15:00', '12:15:00', 3),
('Tuesday',   '09:00:00', '10:00:00', 1),
('Tuesday',   '10:00:00', '11:00:00', 2),
('Wednesday', '09:00:00', '10:00:00', 1),
('Wednesday', '11:15:00', '13:15:00', 3);  -- 2-hour lab slot

-- ---------------------------------------------------------------------
-- 12. TIMETABLE
-- ---------------------------------------------------------------------
INSERT INTO timetable (section_id, course_id, faculty_id, slot_id, academic_year, semester) VALUES
(1, 1, 1, 1, '2025-2026', 3),  -- CSE-A, DBMS, Rohan Shah, Mon 9-10
(1, 2, 2, 2, '2025-2026', 3),  -- CSE-A, OS, Aditi Patel, Mon 10-11
(1, 3, 1, 7, '2025-2026', 3),  -- CSE-A, DBMS Lab, Rohan Shah, Wed 11:15-13:15
(2, 1, 1, 4, '2025-2026', 3),  -- CSE-B, DBMS, Rohan Shah, Tue 9-10
(3, 5, 3, 5, '2025-2026', 2);  -- ECE-A, Digital Electronics, Sanjay Kumar, Tue 10-11

-- ---------------------------------------------------------------------
-- 13. ROOM_ALLOCATION
-- ---------------------------------------------------------------------
INSERT INTO room_allocation (timetable_id, room_type, classroom_id, lab_id) VALUES
(1, 'Classroom', 1, NULL),   -- DBMS lecture -> A-101
(2, 'Classroom', 2, NULL),   -- OS lecture -> A-102
(3, 'Laboratory', NULL, 1),  -- DBMS Lab -> L-301
(4, 'Classroom', 3, NULL),   -- CSE-B DBMS -> B-201
(5, 'Classroom', 1, NULL);   -- ECE Digital Electronics -> A-101

-- ---------------------------------------------------------------------
-- 14. FACULTY_WORKLOAD
-- ---------------------------------------------------------------------
INSERT INTO faculty_workload (faculty_id, academic_year, semester, total_hours_assigned, max_hours_allowed) VALUES
(1, '2025-2026', 3, 5, 18),
(2, '2025-2026', 3, 3, 20),
(3, '2025-2026', 2, 3, 16),
(4, '2025-2026', 4, 0, 22);

-- ---------------------------------------------------------------------
-- 15. CONSTRAINTS_TABLE
-- ---------------------------------------------------------------------
INSERT INTO constraints_table (constraint_type, faculty_id, classroom_id, lab_id, slot_id, description) VALUES
('Faculty_Unavailability', 3, NULL, NULL, 6, 'Dr. Sanjay Kumar attends department meeting every Wednesday 9-10 AM'),
('Room_Unavailability',    NULL, 3, NULL, 3, 'Room B-201 reserved for placement drive on Monday 11:15-12:15'),
('Preferred_Slot',         1, NULL, NULL, 1, 'Prof. Rohan Shah prefers morning slots for lecture-heavy courses');

-- ---------------------------------------------------------------------
-- 16. AUDIT_LOGS  (sample entries)
-- ---------------------------------------------------------------------
INSERT INTO audit_logs (user_id, action_type, table_name, record_id, old_value, new_value) VALUES
(1, 'INSERT', 'timetable', 1, NULL, JSON_OBJECT('section_id', 1, 'course_id', 1, 'faculty_id', 1, 'slot_id', 1)),
(2, 'UPDATE', 'faculty_workload', 1, JSON_OBJECT('total_hours_assigned', 3), JSON_OBJECT('total_hours_assigned', 5));
