import pytest

def test_get_dashboard_stats(client):
    """
    Tests the GET /stats analytics endpoint.
    """
    response = client.get("/api/v1/timetable/stats?academic_year=2025-2026")
    assert response.status_code == 200
    
    data = response.json()
    assert "faculty_count" in data
    assert "course_count" in data
    assert "section_count" in data
    assert "today_classes_count" in data
    assert data["faculty_count"] == 1
    assert data["course_count"] == 1
    assert data["section_count"] == 1

def test_validate_entry_api_clean(client):
    """
    Tests POST /validate-entry when the proposed booking is valid.
    """
    payload = {
        "section_id": 1,
        "course_id": 1,
        "faculty_id": 1,
        "slot_id": 1,
        "room_id": 1,
        "room_type": "Classroom",
        "academic_year": "2025-2026"
    }
    response = client.post("/api/v1/timetable/validate-entry", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["is_valid"] is True
    assert len(data["conflicts"]) == 0

def test_validate_entry_api_conflict(client):
    """
    Tests POST /validate-entry returns conflicts when capacity is violated.
    """
    # Propose section size 60 (Section 1) in Laboratory 1 (Capacity 40)
    payload = {
        "section_id": 1,
        "course_id": 1,
        "faculty_id": 1,
        "slot_id": 1,
        "room_id": 1,
        "room_type": "Laboratory",
        "academic_year": "2025-2026"
    }
    response = client.post("/api/v1/timetable/validate-entry", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["is_valid"] is False
    assert len(data["conflicts"]) > 0
    assert data["conflicts"][0]["type"] == "Capacity_Violation"

def test_generate_timetable_api(client):
    """
    Tests POST /generate schedules dynamically.
    """
    response = client.post("/api/v1/timetable/generate?academic_year=2025-2026")
    assert response.status_code == 200
    
    data = response.json()
    assert "generated" in data["message"]

def test_get_workload_report(client):
    """
    Tests the GET /reports/workload endpoint.
    """
    response = client.get("/api/v1/reports/workload?academic_year=2025-2026")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    assert data[0]["employee_code"] == "FAC101"
    assert "utilization_percentage" in data[0]

def test_get_utilization_report(client):
    """
    Tests the GET /reports/utilization endpoint.
    """
    response = client.get("/api/v1/reports/utilization?academic_year=2025-2026")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    assert data[0]["room_number"] in ["A-101", "L-301"]
    assert "utilization_percentage" in data[0]
