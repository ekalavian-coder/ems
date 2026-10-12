from datetime import date
from app.db.database import get_connection

class EmployeeRepository:
    """Synchronous data-access layer. SQL values are always parameterized."""

    COLUMNS = ("id", "employee_code", "first_name", "last_name", "email",
               "department", "job_title", "joining_date", "probation_end_date",
               "created_at", "updated_at")

    @staticmethod
    def _d(value):
        return value.isoformat() if hasattr(value, "isoformat") else value

    def _row_to_dict(self, row):
        if row is None:
            return None
        result = dict(zip(self.COLUMNS, row))
        for field in ("joining_date", "probation_end_date", "created_at", "updated_at"):
            value = result.get(field)
            if hasattr(value, "isoformat"):
                result[field] = value
        return result

    def list(self, search: str | None = None, department: str | None = None):
        sql = ("SELECT id, employee_code, first_name, last_name, email, department, "
               "job_title, joining_date, probation_end_date, created_at, updated_at "
               "FROM employees")
        params = []
        clauses = []
        if search:
            clauses.append("(LOWER(first_name) LIKE ? OR LOWER(last_name) LIKE ? "
                           "OR LOWER(employee_code) LIKE ? OR LOWER(email) LIKE ?)")
            needle = f"%{search.lower()}%"
            params.extend([needle, needle, needle, needle])
        if department:
            clauses.append("LOWER(department) = LOWER(?)")
            params.append(department)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql +=" ORDER BY last_name, first_name LIMIT 500"
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(sql, params)
                return [self._row_to_dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()
        finally:
            connection.close()

    def get(self, employee_id: int):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT id, employee_code, first_name, last_name, email, department, "
                    "job_title, joining_date, probation_end_date, created_at, updated_at "
                    "FROM employees WHERE id = ?", [employee_id]
                )
                return self._row_to_dict(cursor.fetchone())
            finally:
                cursor.close()
        finally:
            connection.close()

    def create(self, data: dict):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO employees (employee_code, first_name, last_name, email, department, "
                    "job_title, joining_date, probation_end_date, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    [data["employee_code"], data["first_name"], data["last_name"], data["email"],
                     data["department"], data["job_title"], self._d(data["joining_date"]), self._d(data.get("probation_end_date"))]
                )
            finally:
                cursor.close()
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        # Read by unique employee_code to return generated ID and timestamps.
        return self.get_by_code(data["employee_code"])

    def get_by_code(self, employee_code: str):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT id, employee_code, first_name, last_name, email, department, "
                    "job_title, joining_date, probation_end_date, created_at, updated_at "
                    "FROM employees WHERE employee_code = ?", [employee_code]
                )
                return self._row_to_dict(cursor.fetchone())
            finally:
                cursor.close()
        finally:
            connection.close()

    def update(self, employee_id: int, data: dict):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE employees SET employee_code=?, first_name=?, last_name=?, email=?, "
                    "department=?, job_title=?, joining_date=?, probation_end_date=?, "
                    "updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    [data["employee_code"], data["first_name"], data["last_name"], data["email"],
                     data["department"], data["job_title"], self._d(data["joining_date"]),
                     self._d(data.get("probation_end_date")), employee_id]
                )
                changed = cursor.rowcount
            finally:
                cursor.close()
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get(employee_id) if changed else None

    def update_probation_date(self, employee_id: int, probation_end_date: date | None):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE employees SET probation_end_date=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    [self._d(probation_end_date), employee_id]
                )
                changed = cursor.rowcount
            finally:
                cursor.close()
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get(employee_id) if changed else None

    def delete(self, employee_id: int) -> bool:
        connection = get_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM employees WHERE id = ?", [employee_id])
                changed = cursor.rowcount
            finally:
                cursor.close()
            connection.commit()
            return bool(changed)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
