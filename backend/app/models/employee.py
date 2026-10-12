from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class EmployeeBase(BaseModel):
    employee_code: str = Field(min_length=2, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    department: str = Field(min_length=1, max_length=100)
    job_title: str = Field(min_length=1, max_length=100)
    joining_date: date

class EmployeeCreate(EmployeeBase):
    probation_end_date: date | None = None
    hr_verified: bool = False

class EmployeeUpdate(EmployeeBase):
    probation_end_date: date | None = None
    hr_verified: bool = False

class ProbationDateUpdate(BaseModel):
    probation_end_date: date | None = None

class HrVerifiedUpdate(BaseModel):
    hr_verified: bool

class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    probation_end_date: date | None
    hr_verified: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
