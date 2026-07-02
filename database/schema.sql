-- =====================================================================
-- College Time Table Allocation System — Database Schema
-- Engine   : MySQL 8.0+
-- Normal   : 3rd Normal Form (3NF)
-- Author   : Generated for final-year Software Engineering project
-- =====================================================================

CREATE DATABASE IF NOT EXISTS timetable_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE timetable_db;

SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================================
-- 1. DEPARTMENTS  (support table — required for 3NF; avoids repeating
--    department names as free text in Faculty / Courses / Sections)
-- =====================================================================
DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
    department_id     INT AUTO_INCREMENT PRIMARY KEY,
    department_code   VARCHAR(10)  NOT NULL,
    department_name   VARCHAR(100) NOT NULL,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_department_code UNIQUE (department_code),
    CONSTRAINT uq_department_name UNIQUE (department_name)
) ENGINE=InnoDB;


-- =====================================================================
-- 2. USERS  (authentication for all system actors)
-- =====================================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(50)  NOT NULL,
    email          VARCHAR(100) NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    role           ENUM('admin','hod','faculty','student') NOT NULL,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email    UNIQUE (email)
) ENGINE=InnoDB;

CREATE INDEX idx_users_role ON users(role);


-- =====================================================================
-- 3. FACULTY
-- =====================================================================
DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty (
    faculty_id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id              INT NOT NULL,
    employee_code        VARCHAR(20) NOT NULL,
    first_name           VARCHAR(50) NOT NULL,
    last_name            VARCHAR(50) NOT NULL,
    department_id        INT NOT NULL,
    designation          ENUM('Professor','Associate Professor','Assistant Professor','Lecturer') NOT NULL,
    max_hours_per_week   INT DEFAULT 18,
    phone                VARCHAR(15),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_faculty_user_id       UNIQUE (user_id),
    CONSTRAINT uq_faculty_employee_code UNIQUE (employee_code),

    CONSTRAINT fk_faculty_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_faculty_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_faculty_department ON faculty(department_id);


-- =====================================================================
-- 4. LTPSC  (master reference of Lecture-Tutorial-Practical-Self study-
--    Credit patterns, reused across many courses — normalization support)
-- =====================================================================
DROP TABLE IF EXISTS ltpsc;
CREATE TABLE ltpsc (
    ltpsc_id          INT AUTO_INCREMENT PRIMARY KEY,
    lecture_hours     TINYINT UNSIGNED NOT NULL DEFAULT 0,   -- L
    tutorial_hours    TINYINT UNSIGNED NOT NULL DEFAULT 0,   -- T
    practical_hours   TINYINT UNSIGNED NOT NULL DEFAULT 0,   -- P
    self_study_hours  TINYINT UNSIGNED NOT NULL DEFAULT 0,   -- S
    credits           DECIMAL(3,1) NOT NULL,                 -- C

    CONSTRAINT uq_ltpsc_pattern UNIQUE (lecture_hours, tutorial_hours, practical_hours, self_study_hours, credits)
) ENGINE=InnoDB;


-- =====================================================================
-- 5. COURSES
--    Stores Course Code, Course Name, L, T, P, S, Credits (via LTPSC FK),
--    and Theory/Lab type, as required.
-- =====================================================================
DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
    course_id      INT AUTO_INCREMENT PRIMARY KEY,
    course_code    VARCHAR(15)  NOT NULL,
    course_name    VARCHAR(150) NOT NULL,
    department_id  INT NOT NULL,
    ltpsc_id       INT NOT NULL,
    course_type    ENUM('Theory','Lab','Theory+Lab') NOT NULL,
    semester       TINYINT UNSIGNED NOT NULL,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_courses_code UNIQUE (course_code),

    CONSTRAINT fk_courses_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_courses_ltpsc
        FOREIGN KEY (ltpsc_id) REFERENCES ltpsc(ltpsc_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_courses_department ON courses(department_id);
CREATE INDEX idx_courses_semester   ON courses(semester);


-- =====================================================================
-- 6. FACULTY_SUBJECT  (M:N — which faculty can/does teach which course)
-- =====================================================================
DROP TABLE IF EXISTS faculty_subject;
CREATE TABLE faculty_subject (
    faculty_subject_id  INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id          INT NOT NULL,
    course_id           INT NOT NULL,
    academic_year       VARCHAR(9) NOT NULL,   -- e.g. '2025-2026'

    CONSTRAINT uq_faculty_course_year UNIQUE (faculty_id, course_id, academic_year),

    CONSTRAINT fk_facsub_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_facsub_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_facsub_course ON faculty_subject(course_id);


-- =====================================================================
-- 7. SECTIONS  (e.g. CSE-A, ECE-B — a batch of students for a semester)
-- =====================================================================
DROP TABLE IF EXISTS sections;
CREATE TABLE sections (
    section_id        INT AUTO_INCREMENT PRIMARY KEY,
    section_name      VARCHAR(20) NOT NULL,
    department_id     INT NOT NULL,
    semester          TINYINT UNSIGNED NOT NULL,
    academic_year     VARCHAR(9) NOT NULL,
    student_strength  INT DEFAULT 0,
    class_advisor_id  INT NULL,

    CONSTRAINT uq_section_year UNIQUE (section_name, academic_year),

    CONSTRAINT fk_sections_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_sections_advisor
        FOREIGN KEY (class_advisor_id) REFERENCES faculty(faculty_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_sections_department ON sections(department_id);


-- =====================================================================
-- 8. STUDENTS
-- =====================================================================
DROP TABLE IF EXISTS students;
CREATE TABLE students (
    student_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    roll_number     VARCHAR(20) NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    section_id      INT NOT NULL,
    department_id   INT NOT NULL,
    admission_year  YEAR NOT NULL,

    CONSTRAINT uq_students_user_id     UNIQUE (user_id),
    CONSTRAINT uq_students_roll_number UNIQUE (roll_number),

    CONSTRAINT fk_students_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_students_section
        FOREIGN KEY (section_id) REFERENCES sections(section_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_students_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_students_section ON students(section_id);


-- =====================================================================
-- 9. CLASSROOMS
-- =====================================================================
DROP TABLE IF EXISTS classrooms;
CREATE TABLE classrooms (
    classroom_id    INT AUTO_INCREMENT PRIMARY KEY,
    room_number     VARCHAR(20) NOT NULL,
    building        VARCHAR(50) NOT NULL,
    floor           TINYINT NOT NULL,
    capacity        INT NOT NULL,
    has_projector   BOOLEAN DEFAULT FALSE,
    is_available    BOOLEAN DEFAULT TRUE,

    CONSTRAINT uq_classroom_room_number UNIQUE (room_number)
) ENGINE=InnoDB;


-- =====================================================================
-- 10. LABORATORIES
-- =====================================================================
DROP TABLE IF EXISTS laboratories;
CREATE TABLE laboratories (
    lab_id             INT AUTO_INCREMENT PRIMARY KEY,
    lab_number         VARCHAR(20) NOT NULL,
    building           VARCHAR(50) NOT NULL,
    floor              TINYINT NOT NULL,
    capacity           INT NOT NULL,
    lab_type           VARCHAR(50) NOT NULL,   -- e.g. 'Computer Lab', 'Electronics Lab'
    equipment_details  TEXT,
    is_available       BOOLEAN DEFAULT TRUE,

    CONSTRAINT uq_lab_number UNIQUE (lab_number)
) ENGINE=InnoDB;


-- =====================================================================
-- 11. TIME_SLOTS  (support table — required for 3NF; avoids repeating
--     raw day/start_time/end_time values on every Timetable row)
-- =====================================================================
DROP TABLE IF EXISTS time_slots;
CREATE TABLE time_slots (
    slot_id       INT AUTO_INCREMENT PRIMARY KEY,
    day_of_week   ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
    start_time    TIME NOT NULL,
    end_time      TIME NOT NULL,
    slot_order    TINYINT NOT NULL,   -- 1st period, 2nd period...

    CONSTRAINT uq_slot_day_start UNIQUE (day_of_week, start_time),
    CONSTRAINT chk_slot_time CHECK (end_time > start_time)
) ENGINE=InnoDB;


-- =====================================================================
-- 12. TIMETABLE  (the generated schedule: which section studies which
--     course, taught by which faculty, in which slot)
-- =====================================================================
DROP TABLE IF EXISTS timetable;
CREATE TABLE timetable (
    timetable_id    INT AUTO_INCREMENT PRIMARY KEY,
    section_id      INT NOT NULL,
    course_id       INT NOT NULL,
    faculty_id      INT NOT NULL,
    slot_id         INT NOT NULL,
    academic_year   VARCHAR(9) NOT NULL,
    semester        TINYINT UNSIGNED NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- A section cannot have two different courses in the same slot
    CONSTRAINT uq_timetable_section_slot UNIQUE (section_id, slot_id, academic_year),

    -- A faculty member cannot teach two classes in the same slot
    CONSTRAINT uq_timetable_faculty_slot UNIQUE (faculty_id, slot_id, academic_year),

    CONSTRAINT fk_timetable_section
        FOREIGN KEY (section_id) REFERENCES sections(section_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_timetable_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_timetable_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_timetable_slot
        FOREIGN KEY (slot_id) REFERENCES time_slots(slot_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_timetable_course  ON timetable(course_id);
CREATE INDEX idx_timetable_faculty ON timetable(faculty_id);
CREATE INDEX idx_timetable_slot    ON timetable(slot_id);


-- =====================================================================
-- 13. ROOM_ALLOCATION  (assigns a Classroom OR a Laboratory to a
--     Timetable entry — kept separate since rooms/labs are different
--     entities with different attributes)
-- =====================================================================
DROP TABLE IF EXISTS room_allocation;
CREATE TABLE room_allocation (
    room_allocation_id  INT AUTO_INCREMENT PRIMARY KEY,
    timetable_id        INT NOT NULL,
    room_type           ENUM('Classroom','Laboratory') NOT NULL,
    classroom_id        INT NULL,
    lab_id               INT NULL,

    CONSTRAINT uq_room_allocation_timetable UNIQUE (timetable_id),

    CONSTRAINT fk_roomalloc_timetable
        FOREIGN KEY (timetable_id) REFERENCES timetable(timetable_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_roomalloc_classroom
        FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_roomalloc_lab
        FOREIGN KEY (lab_id) REFERENCES laboratories(lab_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_room_allocation_exclusive CHECK (
        (room_type = 'Classroom' AND classroom_id IS NOT NULL AND lab_id IS NULL) OR
        (room_type = 'Laboratory' AND lab_id IS NOT NULL AND classroom_id IS NULL)
    )
) ENGINE=InnoDB;

CREATE INDEX idx_roomalloc_classroom ON room_allocation(classroom_id);
CREATE INDEX idx_roomalloc_lab       ON room_allocation(lab_id);


-- =====================================================================
-- 14. FACULTY_WORKLOAD  (tracked/derived teaching-hour load per faculty
--     per semester — used by scheduler to avoid overloading faculty)
-- =====================================================================
DROP TABLE IF EXISTS faculty_workload;
CREATE TABLE faculty_workload (
    workload_id           INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id             INT NOT NULL,
    academic_year          VARCHAR(9) NOT NULL,
    semester               TINYINT UNSIGNED NOT NULL,
    total_hours_assigned   INT DEFAULT 0,
    max_hours_allowed      INT NOT NULL,
    updated_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_workload_faculty_term UNIQUE (faculty_id, academic_year, semester),

    CONSTRAINT fk_workload_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_workload_hours CHECK (
        total_hours_assigned >= 0 AND max_hours_allowed >= 0
    )
) ENGINE=InnoDB;


-- =====================================================================
-- 15. CONSTRAINTS  (scheduling constraints: faculty unavailability,
--     room unavailability, preferred slots, etc. — feeds the scheduler)
-- =====================================================================
DROP TABLE IF EXISTS constraints_table;
CREATE TABLE constraints_table (
    constraint_id     INT AUTO_INCREMENT PRIMARY KEY,
    constraint_type   ENUM('Faculty_Unavailability','Room_Unavailability','Preferred_Slot','Section_Break') NOT NULL,
    faculty_id        INT NULL,
    classroom_id      INT NULL,
    lab_id            INT NULL,
    slot_id           INT NULL,
    description       VARCHAR(255),
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_constraints_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_constraints_classroom
        FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_constraints_lab
        FOREIGN KEY (lab_id) REFERENCES laboratories(lab_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_constraints_slot
        FOREIGN KEY (slot_id) REFERENCES time_slots(slot_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_constraints_exclusivity CHECK (
        (constraint_type = 'Faculty_Unavailability' AND faculty_id IS NOT NULL AND classroom_id IS NULL AND lab_id IS NULL) OR
        (constraint_type = 'Room_Unavailability' AND faculty_id IS NULL AND (classroom_id IS NOT NULL OR lab_id IS NOT NULL)) OR
        (constraint_type = 'Preferred_Slot' AND faculty_id IS NOT NULL AND classroom_id IS NULL AND lab_id IS NULL) OR
        (constraint_type = 'Section_Break' AND faculty_id IS NULL AND classroom_id IS NULL AND lab_id IS NULL)
    )
) ENGINE=InnoDB;

CREATE INDEX idx_constraints_type ON constraints_table(constraint_type);


-- =====================================================================
-- 16. AUDIT_LOGS  (tracks INSERT/UPDATE/DELETE actions for accountability)
-- =====================================================================
DROP TABLE IF EXISTS audit_logs;
CREATE TABLE audit_logs (
    audit_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NULL,
    action_type      ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    table_name       VARCHAR(50) NOT NULL,
    record_id        INT NOT NULL,
    old_value        JSON NULL,
    new_value        JSON NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_audit_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_timestamp    ON audit_logs(action_timestamp);

SET FOREIGN_KEY_CHECKS = 1;
