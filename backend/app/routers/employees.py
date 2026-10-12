from datetime import date
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from app.models.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, ProbationDateUpdate
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])

def get_service():
    return EmployeeService()

def require_hr(x_user_role: str | None = Header(default=None, alias="X-User-Role")):
    # Demo only. Replace with a trusted role from verified OIDC/JWT claims.
    if x_user_role != "HR":
        raise HTTPException(status_code=403, detail={"code": "HR_ROLE_REQUIRED", "message": "HR role required"})
    return x_user_role

@router.get("", response_model=list[EmployeeResponse])
def list_employees(search: str | None = Query(default=None, max_length=100), service: EmployeeService = Depends(get_service)):
    return service.list_employees(search)

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, service: EmployeeService = Depends(get_service)):
    return service.get_employee(employee_id)

@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, service: EmployeeService = Depends(get_service)):
    return service.create_employee(payload.model_dump())

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    service: EmployeeService = Depends(get_service),
):
    return service.update_employee(employee_id, payload.model_dump(), allow_probation_edit=(x_user_role == "HR"))

@router.patch("/{employee_id}/probation-end-date", response_model=EmployeeResponse)
def update_probation_end_date(
    employee_id: int,
    payload: ProbationDateUpdate,
    _role: str = Depends(require_hr),
    service: EmployeeService = Depends(get_service),
):
    return service.update_probation_date(employee_id, payload.probation_end_date)

@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_employee(employee_id: int, service: EmployeeService = Depends(get_service)):
    return service.delete_employee(employee_id)
