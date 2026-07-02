const API_BASE_URL = "http://127.0.0.1:8000/api/v1/courses";
const HELPER_BASE_URL = "http://127.0.0.1:8000/api/v1/faculty/helper";

const CourseAPI = {
    async getAll(search = "", departmentId = "", semester = "", courseType = "", academicYear = "2025-2026") {
        let url = `${API_BASE_URL}/?academic_year=${encodeURIComponent(academicYear)}&`;
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (departmentId) url += `department_id=${encodeURIComponent(departmentId)}&`;
        if (semester) url += `semester=${encodeURIComponent(semester)}&`;
        if (courseType) url += `course_type=${encodeURIComponent(courseType)}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch courses list");
        }
        return await response.json();
    },

    async getDetails(courseId, academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/${courseId}?academic_year=${encodeURIComponent(academicYear)}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch course details");
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
            throw new Error(err.detail || "Failed to create course");
        }
        return await response.json();
    },

    async update(courseId, data) {
        const response = await fetch(`${API_BASE_URL}/${courseId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to update course");
        }
        return await response.json();
    },

    async delete(courseId, academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/${courseId}?academic_year=${encodeURIComponent(academicYear)}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to delete course");
        }
        return true;
    },

    async getFacultyList() {
        const response = await fetch(`${API_BASE_URL}/helper/faculty`);
        if (!response.ok) {
            throw new Error("Failed to load faculty helpers");
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
export default CourseAPI;
