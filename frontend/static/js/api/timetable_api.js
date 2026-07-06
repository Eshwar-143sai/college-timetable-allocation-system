import { API_ROOT } from "../config.js";
const API_BASE_URL = `${API_ROOT}/api/v1/timetable`;
const SECTIONS_URL = `${API_ROOT}/api/v1/sections`;
const FACULTY_URL = `${API_ROOT}/api/v1/faculty`;
const ROOMS_URL = `${API_ROOT}/api/v1/rooms`;

const TimetableAPI = {
    async generate(academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/generate?academic_year=${encodeURIComponent(academicYear)}`, {
            method: "POST"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to generate timetable");
        }
        return await response.json();
    },

    async get(filters = {}) {
        const academicYear = filters.academic_year || "2025-2026";
        let url = `${API_BASE_URL}/?academic_year=${encodeURIComponent(academicYear)}&`;
        if (filters.section_id) url += `section_id=${encodeURIComponent(filters.section_id)}&`;
        if (filters.faculty_id) url += `faculty_id=${encodeURIComponent(filters.faculty_id)}&`;
        if (filters.classroom_id) url += `classroom_id=${encodeURIComponent(filters.classroom_id)}&`;
        if (filters.lab_id) url += `lab_id=${encodeURIComponent(filters.lab_id)}&`;
        
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch timetable");
        }
        return await response.json();
    },

    async clear(academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/clear?academic_year=${encodeURIComponent(academicYear)}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            throw new Error("Failed to clear timetable");
        }
        return true;
    },

    async getSections(academicYear = "2025-2026") {
        const response = await fetch(`${SECTIONS_URL}/?academic_year=${encodeURIComponent(academicYear)}`);
        if (!response.ok) {
            throw new Error("Failed to load sections");
        }
        return await response.json();
    },

    async getFacultyList() {
        const response = await fetch(`${FACULTY_URL}/`);
        if (!response.ok) {
            throw new Error("Failed to load faculty list");
        }
        return await response.json();
    },

    async getClassrooms() {
        const response = await fetch(`${ROOMS_URL}/classrooms`);
        if (!response.ok) {
            throw new Error("Failed to load classrooms");
        }
        return await response.json();
    },

    async getLaboratories() {
        const response = await fetch(`${ROOMS_URL}/laboratories`);
        if (!response.ok) {
            throw new Error("Failed to load laboratories");
        }
        return await response.json();
    }
};
export default TimetableAPI;
