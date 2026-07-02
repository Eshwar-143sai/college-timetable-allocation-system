import SectionAPI from "../api/section_api.js";

// State
let departments = [];
let advisors = [];
let selectedSectionId = null;
let currentAcademicYear = "2025-2026";

// DOM Elements
const sectionTableBody = document.getElementById("sectionTableBody");
const deptFilterSelect = document.getElementById("deptFilterSelect");
const semFilterSelect = document.getElementById("semFilterSelect");
const addSectionForm = document.getElementById("addSectionForm");
const editSectionForm = document.getElementById("editSectionForm");

// Modals
let addModal, editModal, deleteConfirmModal;

export async function init() {
    try {
        // Initialize Modals
        addModal = new bootstrap.Modal(document.getElementById("addSectionModal"));
        editModal = new bootstrap.Modal(document.getElementById("editSectionModal"));
        deleteConfirmModal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));

        // Load helpers
        departments = await SectionAPI.getDepartments();
        advisors = await SectionAPI.getFacultyList();

        // Populate selections
        populateDropdowns();

        // Load section list
        await loadSectionList();

        // Setup event handlers
        setupEventListeners();

        showToast("Success", "Section Management Module loaded successfully!", "success");
    } catch (err) {
        console.error("Initialization error:", err);
        showToast("Error", "Failed to initialize the sections module", "danger");
    }
}

function populateDropdowns() {
    // Populate Department options
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

    // Populate Advisor options
    const advisorSelects = [
        document.getElementById("addAdvisorSelect"),
        document.getElementById("editAdvisorSelect")
    ];

    advisorSelects.forEach(select => {
        if (!select) return;
        select.innerHTML = '<option value="">Select Class Advisor (Optional)</option>';
        advisors.forEach(adv => {
            select.innerHTML += `<option value="${adv.faculty_id}">${adv.first_name} ${adv.last_name} (${adv.employee_code})</option>`;
        });
    });

    // Populate Section Name options (A-H)
    const nameSelects = [
        document.getElementById("addSectionNameSelect"),
        document.getElementById("editSectionNameSelect")
    ];
    const sectionNames = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    nameSelects.forEach((select, index) => {
        if (!select) return;
        select.innerHTML = index === 0 ? '<option value="" disabled selected>Select Letter</option>' : '';
        sectionNames.forEach(char => {
            select.innerHTML += `<option value="${char}">Section ${char}</option>`;
        });
    });
}

async function loadSectionList() {
    try {
        const deptVal = deptFilterSelect.value;
        const semVal = semFilterSelect.value;

        const sectionsList = await SectionAPI.getAll(deptVal, semVal, currentAcademicYear);
        renderSectionTable(sectionsList);
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderSectionTable(list) {
    if (!sectionTableBody) return;

    if (list.length === 0) {
        sectionTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-5 text-muted">
                    <i class="bi bi-tag fs-1 d-block mb-3 opacity-50"></i>
                    No sections found.
                </td>
            </tr>
        `;
        return;
    }

    sectionTableBody.innerHTML = list.map(section => {
        const deptCode = section.department ? section.department.department_code : "N/A";
        const advisorName = section.advisor 
            ? `${section.advisor.first_name} ${section.advisor.last_name}` 
            : "—";

        // Get only the letter suffix from section_name (e.g. "CSE-A" -> "A")
        const nameParts = section.section_name.split("-");
        const suffixLetter = nameParts[nameParts.length - 1];

        return `
            <tr class="align-middle border-bottom border-light-subtle transition-all hover-bg-light">
                <td>
                    <span class="fw-semibold text-white-85 d-block">${section.section_name}</span>
                    <small class="text-indigo fw-medium">Academic Year: ${section.academic_year}</small>
                </td>
                <td><span class="badge badge-dept">${deptCode}</span></td>
                <td><span class="badge bg-secondary">Semester ${section.semester}</span></td>
                <td><span class="badge badge-indigo">${section.student_strength} Students</span></td>
                <td><span class="text-white-70 fw-medium">${advisorName}</span></td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-icon-glass btn-edit" data-id="${section.section_id}" title="Edit Section">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-sm btn-icon-glass-danger btn-delete" data-id="${section.section_id}" title="Delete Section">
                            <i class="bi bi-trash-fill"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");

    // Bind action buttons
    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", () => openEditModal(btn.dataset.id));
    });
    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", () => openDeleteConfirm(btn.dataset.id));
    });
}

async function openEditModal(sectionId) {
    try {
        selectedSectionId = sectionId;
        const details = await SectionAPI.getDetails(sectionId);

        // Extract raw letter from full name (e.g. "CSE-A" -> "A")
        const nameParts = details.section_name.split("-");
        const suffixLetter = nameParts[nameParts.length - 1];

        document.getElementById("editSectionNameSelect").value = suffixLetter;
        document.getElementById("editDeptSelect").value = details.department_id;
        document.getElementById("editSemester").value = details.semester;
        document.getElementById("editStrength").value = details.student_strength;
        document.getElementById("editAdvisorSelect").value = details.class_advisor_id || "";

        editModal.show();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function openDeleteConfirm(sectionId) {
    selectedSectionId = sectionId;
    deleteConfirmModal.show();
}

function setupEventListeners() {
    // Search Filters
    deptFilterSelect.addEventListener("change", () => loadSectionList());
    semFilterSelect.addEventListener("change", () => loadSectionList());

    // Add Section Submit
    if (addSectionForm) {
        addSectionForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(addSectionForm);
            const rawData = Object.fromEntries(formData.entries());

            const payload = {
                section_name: rawData.section_name,
                department_id: parseInt(rawData.department_id),
                semester: parseInt(rawData.semester),
                academic_year: currentAcademicYear,
                student_strength: parseInt(rawData.student_strength),
                class_advisor_id: rawData.class_advisor_id ? parseInt(rawData.class_advisor_id) : null
            };

            try {
                await SectionAPI.create(payload);
                showToast("Success", "Section created successfully!", "success");
                addSectionForm.reset();
                addModal.hide();
                await loadSectionList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Edit Section Submit
    if (editSectionForm) {
        editSectionForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(editSectionForm);
            const rawData = Object.fromEntries(formData.entries());

            const payload = {
                section_name: rawData.section_name,
                department_id: parseInt(rawData.department_id),
                semester: parseInt(rawData.semester),
                academic_year: currentAcademicYear,
                student_strength: parseInt(rawData.student_strength),
                class_advisor_id: rawData.class_advisor_id ? parseInt(rawData.class_advisor_id) : null
            };

            try {
                await SectionAPI.update(selectedSectionId, payload);
                showToast("Success", "Section updated successfully!", "success");
                editSectionForm.reset();
                editModal.hide();
                await loadSectionList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Confirm Delete
    const btnConfirmDelete = document.getElementById("btnConfirmDelete");
    if (btnConfirmDelete) {
        btnConfirmDelete.addEventListener("click", async () => {
            try {
                await SectionAPI.delete(selectedSectionId);
                showToast("Success", "Section deleted successfully!", "success");
                deleteConfirmModal.hide();
                await loadSectionList();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }
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
