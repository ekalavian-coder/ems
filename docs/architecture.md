# Architecture

Angular single screen → FastAPI router → EmployeeService → EmployeeRepository → H2 JDBC database.

The three Claude Code subagents are development-time agents, not runtime API agents:
- Query Agent: schema/migrations/repository only.
- Service Agent: business rules/DTOs/router/API contract.
- UI Agent: Angular components/forms/client state.
- Main Claude Code session: orchestrator; it plans, approves the contract, delegates in Query → Service → UI order, integrates and verifies. Human review remains mandatory.
