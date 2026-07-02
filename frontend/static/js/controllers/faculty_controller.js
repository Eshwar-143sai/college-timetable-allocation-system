import FacultyAPI from "../api/faculty_api.js";

// Global State
let departments = [];
let courses = [];
let selectedFacultyId = null;

// DOM Elements
const facultyTableBody = document.getElementById("facultyTableBody");
const searchInput = document.getElementById("searchInput");
const deptFilterSelect = document.getElementById("deptFilterSelect");
const addFacultyForm = document.getElementById("addFacultyForm");
const editFacultyForm = document.getElementById("editFacultyForm");
const assignSubjectForm = document.getElementById("assignSubjectForm");

// Modals (Bootstrap instances)
let addModal, editModal, detailsModal, deleteConfirmModal;

export async function init() {
    try {
        // Initialize Modals
        addModal = new bootstrap.Modal(document.getElementById("addFacultyModal"));
        editModal = new bootstrap.Modal(document.getElementById("editFacultyModal"));
        detailsModal = new bootstrap.Modal(document.getElementById("detailsModal"));
        deleteConfirmModal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));

        // Load helpers
        departments = await FacultyAPI.getDepartments();
        courses = await FacultyAPI.getCourses();

        // Populate dropdowns
        populateDropdowns();

        // Load faculty list
        await loadFacultyList();

        // Set up event listeners
        setupEventListeners();
        
        showToast("Success", "Faculty Management Module initialized successfully!", "success");
    } catch (err) {
        console.error("Initialization error:", err);
        showToast("Error", "Failed to initialize the faculty module", "danger");
    }
}

function populateDropdowns() {
    // Populate Department filters and selects
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

    // Populate Courses assign select
    const courseSelect = document.getElementById("assignCourseSelect");
    if (courseSelect) {
        courseSelect.innerHTML = '<option value="" disabled selected>Select Subject</option>';
        courses.forEach(course => {
            courseSelect.innerHTML += `<option value="${course.course_id}">${course.course_name} (${course.course_code}) - Sem ${course.semester}</option>`;
        });
    }
}

async function loadFacultyList() {
    try {
        const searchVal = searchInput.value.trim();
        const deptVal = deptFilterSelect.value;
        const facultyList = await FacultyAPI.getAll(searchVal, deptVal);
        
        renderFacultyTable(facultyList);
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderFacultyTable(list) {
    if (!facultyTableBody) return;
    
    if (list.length === 0) {
        facultyTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-5 text-muted">
                    <i class="bi bi-people fs-1 d-block mb-3 opacity-50"></i>
                    No faculty members found.
                </td>
            </tr>
        `;
        return;
    }

    facultyTableBody.innerHTML = list.map(faculty => {
        const deptCode = faculty.department ? faculty.department.department_code : "N/A";
        return `
            <tr class="align-middle border-bottom border-light-subtle transition-all hover-bg-light">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-circle me-3 text-white d-flex align-items-center justify-content-center fw-bold">
                            ${faculty.first_name[0]}${faculty.last_name[0]}
                        </div>
                        <div>
                            <span class="fw-semibold d-block text-white-85">${faculty.first_name} ${faculty.last_name}</span>
                            <small class="text-muted">${faculty.user ? faculty.user.email : ""}</small>
                        </div>
                    </div>
                </td>
                <td><span class="badge badge-indigo">${faculty.employee_code}</span></td>
                <td><span class="badge badge-dept">${deptCode}</span></td>
                <td><span class="badge badge-role">${faculty.designation}</span></td>
                <td><span class="text-white-70">${faculty.phone || "—"}</span></td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-icon-glass btn-view" data-id="${faculty.faculty_id}" title="View Workload & Subjects">
                            <i class="bi bi-eye-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-icon-glass btn-edit" data-id="${faculty.faculty_id}" title="Edit Profile">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-sm btn-icon-glass-danger btn-delete" data-id="${faculty.faculty_id}" title="Delete Faculty">
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

async function viewDetails(facultyId) {
    try {
        selectedFacultyId = facultyId;
        const details = await FacultyAPI.getDetails(facultyId);
        
        // Populate profile details
        document.getElementById("detailName").textContent = `${details.faculty.first_name} ${details.faculty.last_name}`;
        document.getElementById("detailDesignation").textContent = details.faculty.designation;
        document.getElementById("detailEmail").textContent = details.faculty.user ? details.faculty.user.email : "—";
        document.getElementById("detailPhone").textContent = details.faculty.phone || "—";
        document.getElementById("detailEmpCode").textContent = details.faculty.employee_code;
        document.getElementById("detailDept").textContent = details.faculty.department ? details.faculty.department.department_name : "—";

        // Render Workload Cards
        renderWorkloads(details.workloads);

        // Render Assigned Subjects
        renderSubjects(details.subjects);

        detailsModal.show();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderWorkloads(workloads) {
    const container = document.getElementById("workloadCardsContainer");
    if (!container) return;

    if (workloads.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center text-muted py-3">
                <small>No workloads calculated yet. Assign subjects to calculate workload.</small>
            </div>
        `;
        return;
    }

    container.innerHTML = workloads.map(wl => {
        const percent = Math.min((wl.total_hours_assigned / wl.max_hours_allowed) * 100, 100);
        let progressColor = "bg-success";
        if (percent > 90) progressColor = "bg-danger";
        else if (percent > 70) progressColor = "bg-warning";

        return `
            <div class="col-md-6 mb-3">
                <div class="card card-glass p-3 h-100">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-semibold text-white-70">Sem ${wl.semester} (${wl.academic_year})</span>
                        <span class="badge ${percent > 100 ? 'bg-danger' : 'bg-success'}">
                            ${wl.total_hours_assigned} / ${wl.max_hours_allowed} hrs
                        </span>
                    </div>
                    <div class="progress progress-glass" style="height: 8px;">
                        <div class="progress-bar ${progressColor} progress-bar-striped progress-bar-animated" role="progressbar" style="width: ${percent}%;"></div>
                    </div>
                    <div class="d-flex justify-content-between mt-2">
                        <small class="text-muted">Assigned: ${wl.total_hours_assigned} hrs</small>
                        <small class="text-muted">Max Limit: ${wl.max_hours_allowed} hrs</small>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

function renderSubjects(subjects) {
    const tableBody = document.getElementById("assignedSubjectsTableBody");
    if (!tableBody) return;

    if (subjects.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4 text-muted">
                    No subjects assigned for this faculty.
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = subjects.map(sub => {
        const contactHours = sub.lecture_hours + sub.tutorial_hours + sub.practical_hours;
        return `
            <tr class="align-middle">
                <td><strong class="text-indigo">${sub.course_code}</strong></td>
                <td class="text-white-80">${sub.course_name}</td>
                <td><span class="badge bg-secondary">${sub.academic_year}</span></td>
                <td>Sem ${sub.semester} (${contactHours} Hrs)</td>
                <td>
                    <button class="btn btn-sm btn-icon-glass-danger btn-unassign" 
                            data-course-id="${sub.course_id}" 
                            data-academic-year="${sub.academic_year}" 
                            title="Unassign Subject">
                        <i class="bi bi-x-circle-fill"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");

    // Bind unassign buttons
    document.querySelectorAll(".btn-unassign").forEach(btn => {
        btn.addEventListener("click", () => {
            unassignSubject(selectedFacultyId, btn.dataset.courseId, btn.dataset.academicYear);
        });
    });
}

async function unassignSubject(facultyId, courseId, academicYear) {
    if (!confirm("Are you sure you want to unassign this subject?")) return;
    try {
        await FacultyAPI.unassignSubject(facultyId, courseId, academicYear);
        showToast("Success", "Subject unassigned successfully!", "success");
        // Reload details modal
        await viewDetails(facultyId);
        // Refresh dashboard table
        await loadFacultyList();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function openEditModal(facultyId) {
    try {
        selectedFacultyId = facultyId;
        const details = await FacultyAPI.getDetails(facultyId);
        
        document.getElementById("editFirstName").value = details.faculty.first_name;
        document.getElementById("editLastName").value = details.faculty.last_name;
        document.getElementById("editDeptSelect").value = details.faculty.department_id;
        document.getElementById("editDesignation").value = details.faculty.designation;
        document.getElementById("editPhone").value = details.faculty.phone || "";
        
        editModal.show();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function openDeleteConfirm(facultyId) {
    selectedFacultyId = facultyId;
    deleteConfirmModal.show();
}

function setupEventListeners() {
    // Search & Filter
    searchInput.addEventListener("input", debounce(() => loadFacultyList(), 300));
    deptFilterSelect.addEventListener("change", () => loadFacultyList());

    // Add Faculty Form Submit
    if (addFacultyForm) {
        addFacultyForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(addFacultyForm);
            const data = Object.fromEntries(formData.entries());
            
            try {
                await FacultyAPI.create(data);
                showToast("Success", "Faculty member added successfully!", "success");
                addFacultyForm.reset();
                addModal.hide();
                await loadFacultyList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Edit Faculty Form Submit
    if (editFacultyForm) {
        editFacultyForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(editFacultyForm);
            const data = Object.fromEntries(formData.entries());
            
            try {
                await FacultyAPI.update(selectedFacultyId, data);
                showToast("Success", "Faculty member updated successfully!", "success");
                editModal.hide();
                await loadFacultyList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Assign Subject Form Submit
    if (assignSubjectForm) {
        assignSubjectForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const courseId = document.getElementById("assignCourseSelect").value;
            const academicYear = document.getElementById("assignAcademicYear").value;
            
            if (!courseId || !academicYear) {
                showToast("Validation Error", "Please select a subject and academic year", "warning");
                return;
            }

            try {
                await FacultyAPI.assignSubject(selectedFacultyId, courseId, academicYear);
                showToast("Success", "Subject assigned successfully!", "success");
                assignSubjectForm.reset();
                // Reload details modal & update table
                await viewDetails(selectedFacultyId);
                await loadFacultyList();
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
                await FacultyAPI.delete(selectedFacultyId);
                showToast("Success", "Faculty member deleted successfully!", "success");
                deleteConfirmModal.hide();
                await loadFacultyList();
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
    // Check if toast container exists
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

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toastEl.remove();
    }, 4000);
}
