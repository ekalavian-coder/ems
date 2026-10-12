from datetime import date
import pytest
from fastapi import HTTPException
from app.services.employee_service import EmployeeService

class FakeRepository:
    def __init__(self):
        self.rows = {1: {"id": 1, "employee_code": "E001", "first_name": "Asha", "last_name": "Rao",
                         "email": "asha@example.com", "department": "Engineering", "job_title": "Engineer",
                         "joining_date": date(2024, 1, 1), "probation_end_date": None}}
    def list(self, search=None): return list(self.rows.values())
    def get(self, employee_id): return self.rows.get(employee_id)
    def create(self, data): data = {**data, "id": 2}; self.rows[2] = data; return data
    def update(self, employee_id, data):
        if employee_id not in self.rows: return None
        self.rows[employee_id] = {**data, "id": employee_id}; return self.rows[employee_id]
    def update_probation_date(self, employee_id, value):
        if employee_id not in self.rows: return None
        self.rows[employee_id]["probation_end_date"] = value; return self.rows[employee_id]
    def delete(self, employee_id): return self.rows.pop(employee_id, None) is not None

def test_update_probation_date():
    service = EmployeeService(FakeRepository())
    result = service.update_probation_date(1, date(2024, 4, 1))
    assert result["probation_end_date"] == date(2024, 4, 1)

def test_probation_date_before_joining_date_rejected():
    service = EmployeeService(FakeRepository())
    with pytest.raises(HTTPException) as exc:
        service.update_probation_date(1, date(2023, 12, 31))
    assert exc.value.status_code == 422

def test_missing_employee_returns_404():
    with pytest.raises(HTTPException) as exc:
        EmployeeService(FakeRepository()).get_employee(999)
    assert exc.value.status_code == 404

def test_delete_employee():
    service = EmployeeService(FakeRepository())
    assert service.delete_employee(1)["id"] == 1


def test_non_hr_update_preserves_existing_probation_date():
    repository = FakeRepository()
    repository.rows[1]["probation_end_date"] = date(2024, 4, 1)
    service = EmployeeService(repository)
    data = {"employee_code": "E001", "first_name": "Asha", "last_name": "Rao",
            "email": "asha@example.com", "department": "Engineering", "job_title": "Engineer",
            "joining_date": date(2024, 1, 1), "probation_end_date": date(2024, 6, 1)}
    result = service.update_employee(1, data, allow_probation_edit=False)
    assert result["probation_end_date"] == date(2024, 4, 1)
