# Employee Management MCP Server

This project exposes MCP tools that call the Employee Management REST API. It intentionally does not connect to the database directly: authorization, validation, and business rules stay in the backend API.

## Local setup

```powershell
cd mcp-server
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:EMS_API_BASE_URL = "http://127.0.0.1:8000/api"
$env:EMS_USER_ROLE = "HR" # demo only; do not trust this env-based role in production
python server.py
```

Configure the MCP client to launch `python` with the absolute path to `server.py` as its argument, and set `EMS_API_BASE_URL`. Example Claude Code `.mcp.json` is at the workspace root.

## Tools

- `list_employees`
- `get_employee`
- `create_employee`
- `update_employee`
- `set_probation_end_date` (backend enforces HR-only policy)
- `delete_employee`

The MCP process uses stdio and is intended to be launched by an MCP host. Keep the API running separately.
