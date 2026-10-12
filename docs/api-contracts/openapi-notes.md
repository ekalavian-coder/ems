# Employee API contract (EMS-247)

Base path: `/api/employees`

| Method | Path | Purpose | Authorization |
|---|---|---|---|
| GET | `/` | List employees; optional `?search=` (name/code/email substring) and optional `?department=` (case-insensitive exact match). Both filters combine with AND when supplied. | Demo app access |
| GET | `/{id}` | Get employee | Demo app access |
| POST | `/` | Create employee | Demo app access |
| PUT | `/{id}` | Update employee details | Demo app access |
| PATCH | `/{id}/probation-end-date` | Update nullable probation end date | HR only |
| PATCH | `/{id}/hr-verified` | Set `hr_verified` boolean. Body: `{ "hr_verified": true\|false }` | HR only |
| DELETE | `/{id}` | Delete employee | Demo app access |

Employee JSON fields: `id`, `employee_code`, `first_name`, `last_name`, `email`, `department`, `job_title`, `joining_date`, `probation_end_date` (nullable), `hr_verified` (boolean, defaults to false), `created_at`, `updated_at`.

`hr_verified` is HR-only to write. A non-HR caller on POST or PUT has the incoming value coerced to the current stored value (or `false` on create); only the dedicated PATCH `/{id}/hr-verified` endpoint changes it, and that endpoint rejects non-HR with 403 `HR_ROLE_REQUIRED`.

Errors use FastAPI's `detail` with stable `code` and `message` for business errors. `probation_end_date` must be null or on/after `joining_date`. Demo role enforcement uses `X-User-Role: HR`; production must use verified identity claims.
