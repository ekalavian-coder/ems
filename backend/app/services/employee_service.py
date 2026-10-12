from datetime import date
from fastapi import HTTPException, status
from app.repositories.employee_repository import EmployeeRepository

class EmployeeService:
    def __init__(self, repository: EmployeeRepository | None = None):
        self.repository = repository or EmployeeRepository()

    @staticmethod
    def _normalize(value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    def list_employees(self, search: str | None = None, department: str | None = None):
        return self.repository.list(self._normalize(search), self._normalize(department))

    def get_employee(self, employee_id: int):
        employee = self.repository.get(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        return employee

    def _validate_dates(self, joining_date: date, probation_end_date: date | None):
        if probation_end_date and probation_end_date < joining_date:
            raise HTTPException(
                status_code=422,
                detail={"code": "INVALID_PROBATION_DATE", "message": "Probation end date cannot be before joining date"}
            )

    def create_employee(self, data: dict, allow_hr_verified_edit: bool = False):
        if not allow_hr_verified_edit:
            data["hr_verified"] = False
        self._validate_dates(data["joining_date"], data.get("probation_end_date"))
        try:
            return self.repository.create(data)
        except Exception as exc:
            # Unique constraint violations are normalized without exposing SQL/DB details.
            raise HTTPException(status_code=409, detail={"code": "EMPLOYEE_CONFLICT", "message": "Employee code or email already exists"}) from exc

    def update_employee(self, employee_id: int, data: dict, allow_probation_edit: bool = False, allow_hr_verified_edit: bool = False):
        current = self.repository.get(employee_id)
        if not current:
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        if not allow_probation_edit:
            # Prevent a non-HR caller from bypassing the dedicated PATCH endpoint via PUT.
            data["probation_end_date"] = current.get("probation_end_date")
        if not allow_hr_verified_edit:
            # Repository update() resets a missing key to False, so always carry the stored value.
            data["hr_verified"] = bool(current.get("hr_verified", False))
        self._validate_dates(data["joining_date"], data.get("probation_end_date"))
        try:
            employee =self.repository.update(employee_id, data)
        except Exception as exc:
            raise HTTPException(status_code=409, detail={"code": "EMPLOYEE_CONFLICT", "message": "Employee code or email already exists"}) from exc
        if not employee:
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        return employee

    def update_probation_date(self, employee_id: int, probation_end_date: date | None):
        employee = self.repository.get(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        if probation_end_date and probation_end_date < employee["joining_date"]:
            raise HTTPException(status_code=422, detail={"code": "INVALID_PROBATION_DATE", "message": "Probation end date cannot be before joining date"})
        result = self.repository.update_probation_date(employee_id, probation_end_date)
        if not result:
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        return result

    def update_hr_verified(self, employee_id: int, hr_verified: bool):
        if not self.repository.get(employee_id):
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        result = self.repository.update_hr_verified(employee_id, hr_verified)
        if not result:
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        return result

    def delete_employee(self, employee_id: int):
        if not self.repository.delete(employee_id):
            raise HTTPException(status_code=404, detail={"code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"})
        return {"message": "Employee deleted", "id": employee_id}
