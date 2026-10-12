"""MCP tools for the Employee Management API. Keep business rules in FastAPI."""
import json
import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

API_BASE_URL = os.getenv("EMS_API_BASE_URL", "http://127.0.0.1:8000/api").rstrip("/")
# Demo-only role forwarding. Production must derive identity/role from verified OAuth/JWT claims.
USER_ROLE = os.getenv("EMS_USER_ROLE", "HR")
mcp = FastMCP("employee-management")


def request_api(method: str, path: str = "", *, params: dict | None = None,
                body: dict | None = None, hr_only: bool = False) -> Any:
    headers = {"X-User-Role": USER_ROLE}
    try:
        response = httpx.request(method, f"{API_BASE_URL}{path}", params=params,
                                 json=body, headers=headers, timeout=15.0)
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return {"ok": True}
        return response.json()
    except httpx.HTTPStatusError as exc:
        return {"error": exc.response.status_code, "detail": exc.response.text}
    except httpx.HTTPError as exc:
        return {"error": "api_unavailable", "detail": str(exc)}


@mcp.tool()
def list_employees(search: str = "") -> str:
    """List employees, optionally filtering by name, employee code, or email."""
    result = request_api("GET", "/employees", params={"search": search} if search else None)
    return json.dumps(result, default=str)


@mcp.tool()
def get_employee(employee_id: int) -> str:
    """Get one employee by numeric ID."""
    return json.dumps(request_api("GET", f"/employees/{employee_id}"), default=str)


@mcp.tool()
def create_employee(employee_code: str, first_name: str, last_name: str, email: str,
                    department: str, job_title: str, joining_date: str,
                    probation_end_date: str | None = None) -> str:
    """Create an employee. Dates must be ISO YYYY-MM-DD. Employee code/email must be unique."""
    payload = {"employee_code": employee_code, "first_name": first_name,
               "last_name": last_name, "email": email, "department": department,
               "job_title": job_title, "joining_date": joining_date,
               "probation_end_date": probation_end_date}
    return json.dumps(request_api("POST", "/employees", body=payload), default=str)


@mcp.tool()
def update_employee(employee_id: int, employee_code: str, first_name: str, last_name: str,
                    email: str, department: str, job_title: str, joining_date: str) -> str:
    """Update employee profile fields. Does not change probation end date."""
    payload = {"employee_code": employee_code, "first_name": first_name,
               "last_name": last_name, "email": email, "department": department,
               "job_title": job_title, "joining_date": joining_date}
    current = request_api("GET", f"/employees/{employee_id}")
    if isinstance(current, dict) and current.get("error"):
        return json.dumps(current)
    # Preserve the HR-controlled field when using the full-resource PUT endpoint.
    payload["probation_end_date"] = current.get("probation_end_date")
    return json.dumps(request_api("PUT", f"/employees/{employee_id}", body=payload), default=str)


@mcp.tool()
def set_probation_end_date(employee_id: int, probation_end_date: str | None) -> str:
    """Set or clear probation end date (HR role required). Use ISO YYYY-MM-DD or null."""
    return json.dumps(request_api("PATCH", f"/employees/{employee_id}/probation-end-date",
                                  body={"probation_end_date": probation_end_date}, hr_only=True), default=str)


@mcp.tool()
def delete_employee(employee_id: int) -> str:
    """Delete an employee by numeric ID."""
    return json.dumps(request_api("DELETE", f"/employees/{employee_id}"), default=str)


if __name__ == "__main__":
    mcp.run(transport="stdio")
