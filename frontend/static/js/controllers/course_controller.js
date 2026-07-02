import CourseAPI from "../api/course_api.js";

// State
let departments = [];
let faculties = [];
let selectedCourseId = null;
let currentAcademicYear = "2025-2026";

// DOM Elements
const courseTableBody = document.getElementById("courseTableBody");
const searchInput = document.getElementById("searchInput");
const deptFilterSelect = document.getElementById("deptFilterSelect");
const semFilterSelect = document.getElementById("semFilterSelect");
const typeFilterSelect = document.getElementById("typeFilterSelect");
const addCourseForm = document.getElementById("addCourseForm");
const editCourseForm = document.getElementById("editCourseForm");

// Modals
let addModal, editModal, detailsModal, deleteConfirmModal;

export async function init() {
    try {
        // Initialize Bootstrap Modals
        addModal = new bootstrap.Modal(document.getElementById("addCourseModal"));
        editModal = new bootstrap.Modal(document.getElementById("editCourseModal"));
        detailsModal = new bootstrap.Modal(document.getElementById("detailsModal"));
        deleteConfirmModal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));

        // Load helpers
        departments = await CourseAPI.getDepartments();
        faculties = await CourseAPI.getFacultyList();

        // Populate Dropdowns & Checkbox lists
        populateDropdownsAndChecks();

        // Load courses list
        await loadCourseList();

        // Setup Event Listeners
        setupEventListeners();

        showToast("Success", "Course Management Module loaded successfully!", "success");
    } catch (err) {
        console.error("Initialization error:", err);
        showToast("Error", "Failed to initialize the courses module", "danger");
    }
}

function populateDropdownsAndChecks() {
    // Populate Department selects
    const deptSelects = [
        document.getElementById("deptFilterSelect"),
        document.getElementById("addDeptSelect"),
        document.getElementById("editDeptSelect")
    ];

    deptSelects.forEach((select, index) => {
        if (!select) return;
        select.innerHTML = index === 0 ? '<option value="">All Departments</option>' : '<option value="" disabled selected>Select Department</option>';
        departments.forEach(dept => {
            select.innerHTML += `<option value="${dept.department_id}">${dept.department_name} (${dept.department_code})</option>`;
        });
    });

    // Populate Faculty Checkbox lists (so we can assign multiple faculty members)
    const addFacultyContainer = document.getElementById("addFacultyCheckboxes");
    const editFacultyContainer = document.getElementById("editFacultyCheckboxes");

    const renderCheckboxes = (container, prefix) => {
        if (!container) return;
        if (faculties.length === 0) {
            container.innerHTML = `<small class="text-muted">No faculty members available. Please add faculty first.</small>`;
            return;
        }
        
        container.innerHTML = faculties.map(fac => `
            <div class="form-check col-md-6 mb-2">
                <input class="form-check-input" type="checkbox" name="assigned_faculty" value="${fac.faculty_id}" id="${prefix}Fac_${fac.faculty_id}">
                <label class="form-check-label text-white-80" for="${prefix}Fac_${fac.faculty_id}">
                    ${fac.first_name} ${fac.last_name} (${fac.designation[0]}Prof)
                </label>
            </div>
        `).join("");
    };

    renderCheckboxes(addFacultyContainer, "add");
    renderCheckboxes(editFacultyContainer, "edit");
}

async function loadCourseList() {
    try {
        const searchVal = searchInput.value.trim();
        const deptVal = deptFilterSelect.value;
        const semVal = semFilterSelect.value;
        const typeVal = typeFilterSelect.value;

        const coursesList = await CourseAPI.getAll(searchVal, deptVal, semVal, typeVal, currentAcademicYear);
        renderCourseTable(coursesList);
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderCourseTable(list) {
    if (!courseTableBody) return;

    if (list.length === 0) {
        courseTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5 text-muted">
                    <i class="bi bi-book fs-1 d-block mb-3 opacity-50"></i>
                    No courses found.
                </td>
            </tr>
        `;
        return;
    }

    courseTableBody.innerHTML = list.map(course => {
        const deptCode = course.department ? course.department.department_code : "N/A";
        const facultyNames = course.assigned_faculty.length > 0 
            ? course.assigned_faculty.map(f => `${f.first_name[0]}. ${f.last_name}`).join(", ")
            : "—";

        return `
            <tr class="align-middle border-bottom border-light-subtle transition-all hover-bg-light">
                <td>
                    <span class="fw-semibold text-white-85 d-block">${course.course_name}</span>
                    <small class="text-indigo fw-medium">${course.course_code}</small>
                </td>
                <td><span class="badge badge-dept">${deptCode}</span></td>
                <td><span class="badge bg-secondary">Sem ${course.semester}</span></td>
                <td><span class="badge badge-role">${course.course_type}</span></td>
                <td>
                    <div class="d-flex flex-column">
                        <small class="text-white-70 fw-bold">L-T-P-S: ${course.lecture_hours}-${course.tutorial_hours}-${course.practical_hours}-${course.self_study_hours}</small>
                        <small class="text-muted">Credits: ${course.credits}</small>
                    </div>
                </td>
                <td>
                    <span class="text-white-70 text-truncate d-inline-block" style="max-width: 180px;" title="${facultyNames}">
                        ${facultyNames}
                    </span>
                </td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-icon-glass btn-view" data-id="${course.course_id}" title="View Details">
                            <i class="bi bi-eye-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-icon-glass btn-edit" data-id="${course.course_id}" title="Edit Course">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-sm btn-icon-glass-danger btn-delete" data-id="${course.course_id}" title="Delete Course">
                            <i class="bi bi-trash-fill"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");

    // Bind action buttons
    document.querySelectorAll(".btn-view").forEach(btn => {
        btn.addEventListener("click", () => viewDetails(btn.dataset.id));
    });
    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", () => openEditModal(btn.dataset.id));
    });
    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", () => openDeleteConfirm(btn.dataset.id));
    });
}

async function viewDetails(courseId) {
    try {
        selectedCourseId = courseId;
        const details = await CourseAPI.getDetails(courseId, currentAcademicYear);

        document.getElementById("detailName").textContent = details.course_name;
        document.getElementById("detailCode").textContent = details.course_code;
        document.getElementById("detailType").textContent = details.course_type;
        document.getElementById("detailSem").textContent = `Semester ${details.semester}`;
        document.getElementById("detailDept").textContent = details.department ? details.department.department_name : "—";
        
        // Ltpsc Parameters
        document.getElementById("detailLecture").textContent = details.lecture_hours;
        document.getElementById("detailTutorial").textContent = details.tutorial_hours;
        document.getElementById("detailPractical").textContent = details.practical_hours;
        document.getElementById("detailSelfStudy").textContent = details.self_study_hours;
        document.getElementById("detailCredits").textContent = details.credits;

        // Render Assigned Faculty List
        const facultyListEl = document.getElementById("detailFacultyList");
        if (details.assigned_faculty.length === 0) {
            facultyListEl.innerHTML = `<li class="list-group-item bg-transparent border-light-subtle text-muted text-center py-3">No faculty assigned to this course.</li>`;
        } else {
            facultyListEl.innerHTML = details.assigned_faculty.map(fac => `
                <li class="list-group-item bg-transparent border-light-subtle text-white-80 d-flex justify-content-between align-items-center">
                    <div>
                        <strong class="text-white">${fac.first_name} ${fac.last_name}</strong>
                        <small class="text-muted d-block">${fac.designation} (${fac.employee_code})</small>
                    </div>
                    <span class="badge badge-indigo">Assigned</span>
                </li>
            `).join("");
        }

        detailsModal.show();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function openEditModal(courseId) {
    try {
        selectedCourseId = courseId;
        const details = await CourseAPI.getDetails(courseId, currentAcademicYear);

        document.getElementById("editCourseCode").value = details.course_code;
        document.getElementById("editCourseName").value = details.course_name;
        document.getElementById("editDeptSelect").value = details.department_id;
        document.getElementById("editCourseType").value = details.course_type;
        document.getElementById("editSemester").value = details.semester;
        
        document.getElementById("editLecture").value = details.lecture_hours;
        document.getElementById("editTutorial").value = details.tutorial_hours;
        document.getElementById("editPractical").value = details.practical_hours;
        document.getElementById("editSelfStudy").value = details.self_study_hours;
        document.getElementById("editCredits").value = details.credits;

        // Sync Checkboxes
        const assignedIds = details.assigned_faculty.map(f => f.faculty_id);
        const checkboxes = document.querySelectorAll('input[name="assigned_faculty"][id^="editFac_"]');
        checkboxes.forEach(chk => {
            chk.checked = assignedIds.includes(parseInt(chk.value));
        });

        editModal.show();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function openDeleteConfirm(courseId) {
    selectedCourseId = courseId;
    deleteConfirmModal.show();
}

function setupEventListeners() {
    // Search Filters
    searchInput.addEventListener("input", debounce(() => loadCourseList(), 300));
    deptFilterSelect.addEventListener("change", () => loadCourseList());
    semFilterSelect.addEventListener("change", () => loadCourseList());
    typeFilterSelect.addEventListener("change", () => loadCourseList());

    // Add Course Form Submit
    if (addCourseForm) {
        addCourseForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(addCourseForm);
            const rawData = Object.fromEntries(formData.entries());
            
            // Build assigned faculty array
            const assignedFacultyIds = [];
            const checkboxes = addCourseForm.querySelectorAll('input[name="assigned_faculty"]:checked');
            checkboxes.forEach(chk => assignedFacultyIds.push(parseInt(chk.value)));

            const payload = {
                course_code: rawData.course_code,
                course_name: rawData.course_name,
                department_id: parseInt(rawData.department_id),
                course_type: rawData.course_type,
                semester: parseInt(rawData.semester),
                lecture_hours: parseInt(rawData.lecture_hours),
                tutorial_hours: parseInt(rawData.tutorial_hours),
                practical_hours: parseInt(rawData.practical_hours),
                self_study_hours: parseInt(rawData.self_study_hours),
                credits: parseFloat(rawData.credits),
                assigned_faculty_ids: assignedFacultyIds,
                academic_year: currentAcademicYear
            };

            try {
                await CourseAPI.create(payload);
                showToast("Success", "Course created and faculty workloads updated successfully!", "success");
                addCourseForm.reset();
                addModal.hide();
                await loadCourseList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Edit Course Form Submit
    if (editCourseForm) {
        editCourseForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(editCourseForm);
            const rawData = Object.fromEntries(formData.entries());

            // Build assigned faculty array
            const assignedFacultyIds = [];
            const checkboxes = editCourseForm.querySelectorAll('input[name="assigned_faculty"]:checked');
            checkboxes.forEach(chk => assignedFacultyIds.push(parseInt(chk.value)));

            const payload = {
                course_code: rawData.course_code,
                course_name: rawData.course_name,
                department_id: parseInt(rawData.department_id),
                course_type: rawData.course_type,
                semester: parseInt(rawData.semester),
                lecture_hours: parseInt(rawData.lecture_hours),
                tutorial_hours: parseInt(rawData.tutorial_hours),
                practical_hours: parseInt(rawData.practical_hours),
                self_study_hours: parseInt(rawData.self_study_hours),
                credits: parseFloat(rawData.credits),
                assigned_faculty_ids: assignedFacultyIds,
                academic_year: currentAcademicYear
            };

            try {
                await CourseAPI.update(selectedCourseId, payload);
                showToast("Success", "Course and related workloads updated successfully!", "success");
                editCourseForm.reset();
                editModal.hide();
                await loadCourseList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Confirm Delete Click
    const btnConfirmDelete = document.getElementById("btnConfirmDelete");
    if (btnConfirmDelete) {
        btnConfirmDelete.addEventListener("click", async () => {
            try {
                await CourseAPI.delete(selectedCourseId, currentAcademicYear);
                showToast("Success", "Course deleted and faculty workloads updated successfully!", "success");
                deleteConfirmModal.hide();
                await loadCourseList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }
}

// Helpers
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function showToast(title, message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container position-fixed bottom-0 end-0 p-3";
        document.body.appendChild(container);
    }

    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0 shadow-lg show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <strong class="d-block">${title}</strong>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = toastHtml.trim();
    const toastEl = tempDiv.firstChild;
    container.appendChild(toastEl);

    setTimeout(() => {
        toastEl.remove();
    }, 4000);
}
