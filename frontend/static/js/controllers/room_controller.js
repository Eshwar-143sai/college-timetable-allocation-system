import RoomAPI from "../api/room_api.js";

// State
let selectedRoomId = null;
let currentTab = "classroom"; // "classroom" or "laboratory"

// DOM Elements
const classroomTableBody = document.getElementById("classroomTableBody");
const labTableBody = document.getElementById("labTableBody");

const addClassroomForm = document.getElementById("addClassroomForm");
const editClassroomForm = document.getElementById("editClassroomForm");
const addLabForm = document.getElementById("addLabForm");
const editLabForm = document.getElementById("editLabForm");

const searchBuilding = document.getElementById("searchBuilding");
const availableFilter = document.getElementById("availableFilter");

// Modals
let addClassroomModal, editClassroomModal, addLabModal, editLabModal, deleteConfirmModal;

export async function init() {
    try {
        // Initialize Modals
        addClassroomModal = new bootstrap.Modal(document.getElementById("addClassroomModal"));
        editClassroomModal = new bootstrap.Modal(document.getElementById("editClassroomModal"));
        addLabModal = new bootstrap.Modal(document.getElementById("addLabModal"));
        editLabModal = new bootstrap.Modal(document.getElementById("editLabModal"));
        deleteConfirmModal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));

        // Load active view lists
        await refreshLists();

        // Setup event handlers
        setupEventListeners();

        showToast("Success", "Classroom Management Module initialized successfully!", "success");
    } catch (err) {
        console.error("Initialization error:", err);
        showToast("Error", "Failed to initialize the classroom module", "danger");
    }
}

async function refreshLists() {
    const building = searchBuilding.value.trim();
    const availableVal = availableFilter.value;
    const availableOnly = availableVal === "true" ? true : (availableVal === "false" ? false : null);
    
    try {
        if (currentTab === "classroom") {
            const list = await RoomAPI.getClassrooms(building, availableOnly);
            renderClassroomTable(list);
        } else {
            const list = await RoomAPI.getLaboratories(building, availableOnly);
            renderLabTable(list);
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderClassroomTable(list) {
    if (!classroomTableBody) return;

    if (list.length === 0) {
        classroomTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5 text-muted">
                    <i class="bi bi-door-closed fs-1 d-block mb-3 opacity-50"></i>
                    No classrooms found.
                </td>
            </tr>
        `;
        return;
    }

    classroomTableBody.innerHTML = list.map(room => `
        <tr class="align-middle border-bottom border-light-subtle transition-all hover-bg-light">
            <td><strong class="text-white-85">${room.room_number}</strong></td>
            <td><span class="badge bg-secondary">${room.building}</span></td>
            <td><span class="badge badge-dept">Floor ${room.floor}</span></td>
            <td><span class="badge badge-indigo">${room.capacity} Students</span></td>
            <td>
                <span class="badge ${room.has_projector ? 'bg-success' : 'bg-secondary'}">
                    ${room.has_projector ? 'Yes' : 'No'}
                </span>
            </td>
            <td>
                <span class="badge ${room.is_available ? 'bg-success' : 'bg-danger'}">
                    ${room.is_available ? 'Available' : 'Unavailable'}
                </span>
            </td>
            <td>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-icon-glass btn-edit-classroom" data-id="${room.classroom_id}" title="Edit Classroom">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-sm btn-icon-glass-danger btn-delete-classroom" data-id="${room.classroom_id}" title="Delete Classroom">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join("");

    // Bind events
    document.querySelectorAll(".btn-edit-classroom").forEach(btn => {
        btn.addEventListener("click", () => openEditClassroom(btn.dataset.id));
    });
    document.querySelectorAll(".btn-delete-classroom").forEach(btn => {
        btn.addEventListener("click", () => openDeleteConfirm(btn.dataset.id, "classroom"));
    });
}

function renderLabTable(list) {
    if (!labTableBody) return;

    if (list.length === 0) {
        labTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5 text-muted">
                    <i class="bi bi-cpu fs-1 d-block mb-3 opacity-50"></i>
                    No laboratories found.
                </td>
            </tr>
        `;
        return;
    }

    labTableBody.innerHTML = list.map(lab => `
        <tr class="align-middle border-bottom border-light-subtle transition-all hover-bg-light">
            <td><strong class="text-white-85">${lab.lab_number}</strong></td>
            <td><span class="badge bg-secondary">${lab.building}</span></td>
            <td><span class="badge badge-dept">Floor ${lab.floor}</span></td>
            <td><span class="badge badge-indigo">${lab.capacity} Students</span></td>
            <td><span class="badge badge-role">${lab.lab_type}</span></td>
            <td>
                <span class="badge ${lab.is_available ? 'bg-success' : 'bg-danger'}">
                    ${lab.is_available ? 'Available' : 'Unavailable'}
                </span>
            </td>
            <td>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-icon-glass btn-edit-lab" data-id="${lab.lab_id}" title="Edit Laboratory">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-sm btn-icon-glass-danger btn-delete-lab" data-id="${lab.lab_id}" title="Delete Laboratory">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join("");

    // Bind events
    document.querySelectorAll(".btn-edit-lab").forEach(btn => {
        btn.addEventListener("click", () => openEditLab(btn.dataset.id));
    });
    document.querySelectorAll(".btn-delete-lab").forEach(btn => {
        btn.addEventListener("click", () => openDeleteConfirm(btn.dataset.id, "laboratory"));
    });
}

async function openEditClassroom(id) {
    try {
        selectedRoomId = id;
        const details = await RoomAPI.getClassroomDetails(id);
        
        document.getElementById("editClassroomNumber").value = details.room_number;
        document.getElementById("editClassroomBuilding").value = details.building;
        document.getElementById("editClassroomFloor").value = details.floor;
        document.getElementById("editClassroomCapacity").value = details.capacity;
        document.getElementById("editClassroomProjector").checked = details.has_projector;
        document.getElementById("editClassroomAvailable").checked = details.is_available;

        editClassroomModal.show();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function openEditLab(id) {
    try {
        selectedRoomId = id;
        const details = await RoomAPI.getLaboratoryDetails(id);

        document.getElementById("editLabNumber").value = details.lab_number;
        document.getElementById("editLabBuilding").value = details.building;
        document.getElementById("editLabFloor").value = details.floor;
        document.getElementById("editLabCapacity").value = details.capacity;
        document.getElementById("editLabType").value = details.lab_type;
        document.getElementById("editLabEquipment").value = details.equipment_details || "";
        document.getElementById("editLabAvailable").checked = details.is_available;

        editLabModal.show();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function openDeleteConfirm(id, type) {
    selectedRoomId = id;
    currentTab = type; // Keep track of whether we delete classroom or lab
    deleteConfirmModal.show();
}

function setupEventListeners() {
    // Tab changes
    const tabClassroom = document.getElementById("tabClassroomBtn");
    const tabLab = document.getElementById("tabLabBtn");

    if (tabClassroom && tabLab) {
        tabClassroom.addEventListener("click", () => {
            currentTab = "classroom";
            tabClassroom.classList.add("active");
            tabLab.classList.remove("active");
            document.getElementById("classroomPane").classList.remove("d-none");
            document.getElementById("labPane").classList.add("d-none");
            document.getElementById("btnAddRoomTrigger").innerHTML = '<i class="bi bi-door-closed-fill me-2"></i>Add Classroom';
            refreshLists();
        });

        tabLab.addEventListener("click", () => {
            currentTab = "laboratory";
            tabLab.classList.add("active");
            tabClassroom.classList.remove("active");
            document.getElementById("labPane").classList.remove("d-none");
            document.getElementById("classroomPane").classList.add("d-none");
            document.getElementById("btnAddRoomTrigger").innerHTML = '<i class="bi bi-cpu-fill me-2"></i>Add Laboratory';
            refreshLists();
        });
    }

    // Trigger Add Modal dynamically depending on active tab
    const btnAddRoomTrigger = document.getElementById("btnAddRoomTrigger");
    if (btnAddRoomTrigger) {
        btnAddRoomTrigger.addEventListener("click", () => {
            if (currentTab === "classroom") {
                addClassroomModal.show();
            } else {
                addLabModal.show();
            }
        });
    }

    // Filter events
    searchBuilding.addEventListener("input", debounce(() => refreshLists(), 300));
    availableFilter.addEventListener("change", () => refreshLists());

    // Add Classroom submit
    if (addClassroomForm) {
        addClassroomForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(addClassroomForm);
            const rawData = Object.fromEntries(formData.entries());

            const payload = {
                room_number: rawData.room_number,
                building: rawData.building,
                floor: parseInt(rawData.floor),
                capacity: parseInt(rawData.capacity),
                has_projector: addClassroomForm.querySelector('[name="has_projector"]').checked,
                is_available: true
            };

            try {
                await RoomAPI.createClassroom(payload);
                showToast("Success", "Classroom created successfully!", "success");
                addClassroomForm.reset();
                addClassroomModal.hide();
                await refreshLists();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Edit Classroom submit
    if (editClassroomForm) {
        editClassroomForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(editClassroomForm);
            const rawData = Object.fromEntries(formData.entries());

            const payload = {
                room_number: rawData.room_number,
                building: rawData.building,
                floor: parseInt(rawData.floor),
                capacity: parseInt(rawData.capacity),
                has_projector: editClassroomForm.querySelector('[name="has_projector"]').checked,
                is_available: editClassroomForm.querySelector('[name="is_available"]').checked
            };

            try {
                await RoomAPI.updateClassroom(selectedRoomId, payload);
                showToast("Success", "Classroom updated successfully!", "success");
                editClassroomModal.hide();
                await refreshLists();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Add Lab submit
    if (addLabForm) {
        addLabForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(addLabForm);
            const rawData = Object.fromEntries(formData.entries());

            const payload = {
                lab_number: rawData.lab_number,
                building: rawData.building,
                floor: parseInt(rawData.floor),
                capacity: parseInt(rawData.capacity),
                lab_type: rawData.lab_type,
                equipment_details: rawData.equipment_details || "",
                is_available: true
            };

            try {
                await RoomAPI.createLaboratory(payload);
                showToast("Success", "Laboratory created successfully!", "success");
                addLabForm.reset();
                addLabModal.hide();
                await refreshLists();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Edit Lab submit
    if (editLabForm) {
        editLabForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(editLabForm);
            const rawData = Object.fromEntries(formData.entries());

            const payload = {
                lab_number: rawData.lab_number,
                building: rawData.building,
                floor: parseInt(rawData.floor),
                capacity: parseInt(rawData.capacity),
                lab_type: rawData.lab_type,
                equipment_details: rawData.equipment_details || "",
                is_available: editLabForm.querySelector('[name="is_available"]').checked
            };

            try {
                await RoomAPI.updateLaboratory(selectedRoomId, payload);
                showToast("Success", "Laboratory updated successfully!", "success");
                editLabModal.hide();
                await refreshLists();
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
                if (currentTab === "classroom") {
                    await RoomAPI.deleteClassroom(selectedRoomId);
                } else {
                    await RoomAPI.deleteLaboratory(selectedRoomId);
                }
                showToast("Success", "Room deleted successfully!", "success");
                deleteConfirmModal.hide();
                await refreshLists();
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
