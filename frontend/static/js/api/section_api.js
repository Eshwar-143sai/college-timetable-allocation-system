import { API_ROOT } from "../config.js";
const API_BASE_URL = `${API_ROOT}/api/v1/sections`;
const HELPER_BASE_URL = `${API_ROOT}/api/v1/faculty/helper`;
const FACULTY_BASE_URL = `${API_ROOT}/api/v1/faculty`;

const SectionAPI = {
    async getAll(departmentId = "", semester = "", academicYear = "2025-2026") {
        let url = `${API_BASE_URL}/?academic_year=${encodeURIComponent(academicYear)}&`;
        if (departmentId) url += `department_id=${encodeURIComponent(departmentId)}&`;
        if (semester) url += `semester=${encodeURIComponent(semester)}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch sections list");
        }
        return await response.json();
    },

    async getDetails(sectionId) {
        const response = await fetch(`${API_BASE_URL}/${sectionId}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch section details");
        }
        return await response.json();
    },

    async create(data) {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to create section");
        }
        return await response.json();
    },

    async update(sectionId, data) {
        const response = await fetch(`${API_BASE_URL}/${sectionId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to update section");
        }
        return await response.json();
    },

    async delete(sectionId) {
        const response = await fetch(`${API_BASE_URL}/${sectionId}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to delete section");
        }
        return true;
    },

    async getFacultyList() {
        const response = await fetch(`${FACULTY_BASE_URL}/`);
        if (!response.ok) {
            throw new Error("Failed to load faculty advisors");
        }
        return await response.json();
    },

    async getDepartments() {
        const response = await fetch(`${HELPER_BASE_URL}/departments`);
        if (!response.ok) {
            throw new Error("Failed to load departments");
        }
        return await response.json();
    }
};
export default SectionAPI;
