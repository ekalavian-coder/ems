# Employee API contract (EMS-247)

Base path: `/api/employees`

| Method | Path | Purpose | Authorization |
|---|---|---|---|
| GET | `/` | List employees; optional `?search=` | Demo app access |
| GET | `/{id}` | Get employee | Demo app access |
| POST | `/` | Create employee | Demo app access |
| PUT | `/{id}` | Update employee details | Demo app access |
| PATCH | `/{id}/probation-end-date` | Update nullable probation end date | HR only |
| DELETE | `/{id}` | Delete employee | Demo app access |

Employee JSON fields: `id`, `employee_code`, `first_name`, `last_name`, `email`, `department`, `job_title`, `joining_date`, `probation_end_date` (nullable), `created_at`, `updated_at`.

Errors use FastAPI's `detail` with stable `code` and `message` for business errors. `probation_end_date` must be null or on/after `joining_date`. Demo role enforcement uses `X-User-Role: HR`; production must use verified identity claims.
