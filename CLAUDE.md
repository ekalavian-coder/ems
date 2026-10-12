# Workspace orchestration instructions

This is a multi-project workspace. Treat each directory as a separate project boundary and avoid mixing runtime responsibilities.

## Project ownership
- `frontend/`: Angular UI only; call backend REST API; do not access DB directly.
- `backend/`: FastAPI router/service/repository; owns validation, authorization, and business rules.
- `database-service/`: H2 process, persistence and DB runtime configuration.
- `mcp-server/`: MCP tool definitions; call the backend API only; never connect directly to the DB.

## Agent workflow
1. Main Claude Code session acts as orchestrator. Read ticket and API contract first.
2. Query Agent: database schema/migrations/repository only; report schema and repository contract.
3. Service Agent: backend DTOs, validation, API, auth and tests; align with Query Agent contract.
4. UI Agent: frontend model/client/screen; use only documented REST API.
5. MCP server changes should be delegated as a separate bounded task only after the API contract is stable.
6. Orchestrator checks cross-project consistency, tests, security and documentation before declaring completion.

## Rules
- Do not change API contracts silently. Update `docs/api-contracts/openapi-notes.md` and affected tests.
- Never let UI or MCP code query the database directly.
- SQL parameters must be bound, not interpolated.
- Probation date writes are HR-only; authorization must be enforced by the backend.
- `X-User-Role` is demo-only and must not be treated as production authentication.
- Do not use production employee data or secrets in prompts, logs, fixtures, or tests.
