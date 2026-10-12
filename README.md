# Employee Management — split projects + MCP

This workspace implements EMS-247: add a nullable probation end date to employees, editable by HR only. It is structured so each deployable responsibility can be opened, versioned, tested, and assigned independently.

## Project boundaries

| Project | Responsibility | Run/deploy independently |
|---|---|---|
| `frontend/` | Angular one-screen employee UI; calls REST API only | Node.js 20+, port 4200 |
| `backend/` | Synchronous FastAPI CRUD; router → service → repository; business rules and role enforcement | Python 3.11+, Java 21+, port 8000 |
| `database-service/` | H2 TCP server and persistent database volume | Docker; internal TCP port 9092 |
| `mcp-server/` | MCP tools that call the backend REST API; no direct database access | Python + MCP SDK; launched by an MCP host |

`database-service` is an independent project. SQL schema and versioned migrations are kept under `backend/app/db/schema.sql` and `backend/migrations/` for this demo. In a production setup, move migrations to a dedicated migration project/job and consider PostgreSQL or a managed database instead of H2.

## Recommended: run all app services with Docker Compose

Prerequisite: Docker Desktop running on Windows.

From this workspace root:

```powershell
docker compose up --build
```

Open:
- Angular UI: http://localhost:4200
- FastAPI Swagger: http://localhost:8000/docs
- API health: http://localhost:8000/health

The H2 TCP port is intentionally not published to the host. Data persists in the `h2_data` Docker volume. To stop services, run `docker compose down`. To also remove the demo database, run `docker compose down -v` (destructive).

## Run projects separately (without Docker)

### 1. Start the database service

```powershell
cd database-service
docker build -t ems-database .
docker run --name ems-database -p 9092:9092 -v ems_h2_data:/data ems-database
```

Keep this terminal running. For local development only, this command publishes the DB port to localhost.

### 2. Start the backend

Install a JDK 21 and Node.js 20 LTS separately if they are not installed. Verify with `java -version`, `node -v`, and `npm -v`.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
New-Item -ItemType Directory -Force lib | Out-Null
Invoke-WebRequest -Uri "https://repo.maven.apache.org/maven2/com/h2database/h2/2.3.232/h2-2.3.232.jar" -OutFile ".\lib\h2.jar"
$env:H2_JAR_PATH = (Resolve-Path ".\lib\h2.jar").Path
$env:H2_JDBC_URL = "jdbc:h2:tcp://localhost:9092/./emsdb"
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend

In a new terminal:

```powershell
cd frontend
npm install
npm start
```

### 4. Start the MCP server

In a new terminal after the backend is running:

```powershell
cd mcp-server
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:EMS_API_BASE_URL = "http://127.0.0.1:8000/api"
$env:EMS_USER_ROLE = "HR"
python server.py
```

The MCP server uses stdio and should normally be launched by an MCP client/host. The root `.mcp.json` is an example Claude Code configuration; install the MCP requirements in the Python environment used by the configured command before launching through the host.

## MCP tool surface

- `list_employees`
- `get_employee`
- `create_employee`
- `update_employee`
- `set_probation_end_date` (the backend enforces HR authorization)
- `delete_employee`

The MCP server deliberately calls REST endpoints instead of opening JDBC connections. That means the same API validation, auditing, and authorization path applies to UI and AI-tool calls. Avoid exposing raw SQL as an MCP tool; expose narrowly scoped business operations instead.

## Three coding agents

The `.claude/agents/` files define the Query, Service, and UI coding subagents. They are development-time agents, distinct from the runtime MCP server:

1. Query Agent: schema/migrations/repository and data-access tests.
2. Service Agent: API contract, DTOs, business rules, endpoint tests, authorization.
3. UI Agent: Angular screen and REST client.
4. Main Claude Code session orchestrates the sequence and verifies integration across projects.

Use the workspace root as the orchestrator context and delegate bounded tasks with explicit file ownership. Keep the API contract in `docs/api-contracts/openapi-notes.md` synchronized before parallel work.

## Important security note

This is a local demo. `X-User-Role` is not authentication; the UI role selector and `EMS_USER_ROLE` are intentionally convenient demo wiring only. Before production, use verified OAuth/OIDC/JWT claims, enforce authorization in the backend, configure secrets securely, and do not expose H2's TCP port publicly. Do not use real employee data.
