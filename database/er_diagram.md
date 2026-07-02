# ER Diagram — College Time Table Allocation System (Text Format)

Legend: `PK` = Primary Key, `FK` = Foreign Key, `1—N` = one-to-many, `N—M` = many-to-many, `1—1` = one-to-one

```
┌─────────────────────┐
│   DEPARTMENTS        │
│  PK department_id    │
│     department_code  │
│     department_name  │
└──────────┬───────────┘
           │ 1
           │
           │ N
   ┌───────┼─────────────┬─────────────────┬──────────────────┐
   ▼                     ▼                 ▼                  ▼
┌──────────────┐  ┌─────────────┐  ┌──────────────┐   ┌────────────────┐
│  FACULTY      │  │  COURSES    │  │  SECTIONS     │   │  STUDENTS       │
│ PK faculty_id │  │ PK course_id│  │ PK section_id │   │ PK student_id   │
│ FK user_id ───┼─┐│ FK dept_id  │  │ FK dept_id    │   │ FK user_id  ────┼─┐
│ FK dept_id    │ ││ FK ltpsc_id─┼─┐│               │   │ FK section_id──┼─┼──┐
│    emp_code   │ │└─────────────┘ │└───────┬───────┘   │ FK dept_id      │ │  │
│    designation│ │        │        │        │1          │  roll_number   │ │  │
└──────┬────────┘ │        │N       │        │           └─────────────────┘ │  │
       │1          │        ▼        │        N                              │  │
       │           │  ┌───────────┐  │  ┌──────────────┐                     │  │
       │N          │  │  LTPSC     │  │  │ (students    │                     │  │
┌──────▼────────┐  │  │ PK ltpsc_id│  │  │  belong to   │◄────────────────────┘  │
│FACULTY_SUBJECT│  │  │    L,T,P,S │  │  │  1 section)  │                        │
│PK fac_sub_id  │  │  │    credits │  │  └──────────────┘                        │
│FK faculty_id  │  │  └────────────┘  │                                          │
│FK course_id ──┼──┘                  │                                          │
└───────────────┘                     │                                          │
       ▲ N                            │                                          │
       │                              │                                          │
       │1                             │                                          │
┌──────┴────────┐                     │                                          │
│  USERS         │◄────────────────────────────────────────────────────────────┘
│ PK user_id     │  (1 user —1 faculty  OR  1 user —1 student  OR admin/hod)
│    username    │
│    role        │
└────────────────┘


┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  TIME_SLOTS        │        │  CLASSROOMS       │        │  LABORATORIES      │
│ PK slot_id          │        │ PK classroom_id    │        │ PK lab_id           │
│    day_of_week      │        │    room_number      │        │    lab_number       │
│    start_time       │        │    capacity          │        │    capacity          │
│    end_time         │        │    building           │        │    lab_type          │
└─────────┬───────────┘        └──────────┬──────────┘        └──────────┬──────────┘
          │1                              │1                              │1
          │                               │                               │
          │N                              │N                              │N
          │                    ┌──────────┴───────────────────────────────┘
          │                    │   (Room_Allocation links to EXACTLY ONE of
          │                    │    Classroom OR Laboratory per timetable row)
          ▼                    ▼
   ┌─────────────────────────────────┐
   │           TIMETABLE               │
   │ PK timetable_id                   │
   │ FK section_id  ────────────────►  SECTIONS
   │ FK course_id   ────────────────►  COURSES
   │ FK faculty_id  ────────────────►  FACULTY
   │ FK slot_id     ────────────────►  TIME_SLOTS
   │    academic_year, semester        │
   │  UNIQUE(section_id, slot_id, yr)  │  -- no double-booking a section
   │  UNIQUE(faculty_id, slot_id, yr)  │  -- no double-booking a faculty
   └────────────┬───────────────────────┘
                │ 1
                │
                │ 1
   ┌────────────▼───────────────────┐
   │      ROOM_ALLOCATION             │
   │ PK room_allocation_id            │
   │ FK timetable_id  (UNIQUE)        │
   │ FK classroom_id  (nullable)      │
   │ FK lab_id        (nullable)      │
   │    room_type ENUM                │
   └───────────────────────────────────┘


┌───────────────────┐         ┌────────────────────┐
│  FACULTY_WORKLOAD   │         │  CONSTRAINTS_TABLE    │
│ PK workload_id       │         │ PK constraint_id       │
│ FK faculty_id ───────┼──► FACULTY                       │
│    academic_year     │    FK faculty_id (nullable)  ──► FACULTY
│    semester          │    FK classroom_id (nullable)──► CLASSROOMS
│    total_hours       │    FK lab_id (nullable)      ──► LABORATORIES
│    max_hours         │    FK slot_id (nullable)     ──► TIME_SLOTS
└───────────────────────┘    └────────────────────────────┘


┌────────────────────┐
│   AUDIT_LOGS          │
│ PK audit_id            │
│ FK user_id (nullable) ─┼──► USERS
│    action_type         │
│    table_name          │
│    record_id           │
│    old_value / new_value (JSON) │
└─────────────────────────┘
```

## Relationship Summary

| Relationship | Cardinality | Notes |
|---|---|---|
| Departments → Faculty | 1—N | A department has many faculty members |
| Departments → Courses | 1—N | A department owns many courses |
| Departments → Sections | 1—N | A department has many sections |
| Departments → Students | 1—N | A department has many students |
| Users → Faculty | 1—1 | Each faculty record has exactly one login |
| Users → Students | 1—1 | Each student record has exactly one login |
| LTPSC → Courses | 1—N | Many courses can share the same L-T-P-S-C pattern |
| Faculty ↔ Courses | N—M (via Faculty_Subject) | A faculty can teach many courses; a course can be taught by multiple faculty across sections/years |
| Sections → Students | 1—N | A section contains many students |
| Sections → Timetable | 1—N | A section has many timetable entries (one per class) |
| Courses → Timetable | 1—N | A course appears in many timetable slots (across sections) |
| Faculty → Timetable | 1—N | A faculty member teaches many timetable slots |
| Time_Slots → Timetable | 1—N | A time slot is reused across many days/sections |
| Timetable → Room_Allocation | 1—1 | Each timetable entry has exactly one room assigned |
| Classrooms → Room_Allocation | 1—N | A classroom is used across many timetable entries |
| Laboratories → Room_Allocation | 1—N | A lab is used across many timetable entries |
| Faculty → Faculty_Workload | 1—N | One workload record per faculty per semester |
| Faculty/Classrooms/Labs/Time_Slots → Constraints_Table | 1—N (each, nullable) | A constraint may reference any one of these entities |
| Users → Audit_Logs | 1—N | A user's actions generate many audit log entries |

## Key Design Decisions (3NF Justification)

1. **No transitive dependencies**: e.g., `Courses.department_name` is never stored directly — only `department_id` (FK), so department name changes propagate everywhere via one row update in `Departments`.
2. **No repeating groups**: L/T/P/S/Credits values live once in `LTPSC` and are referenced, not duplicated, across courses that share a pattern.
3. **No partial dependencies on composite keys**: Junction tables (`Faculty_Subject`, `Room_Allocation`) store only foreign keys + attributes that depend on the *whole* combination (e.g., `academic_year` in `Faculty_Subject` depends on the faculty-course pair, not on either alone).
4. **Every non-key attribute depends on the whole key, only the key, nothing but the key.**
