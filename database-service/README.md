# Database Service — H2

This is a separately deployable H2 TCP database service. The API connects over JDBC using `jdbc:h2:tcp://database:9092/./emsdb` in Docker Compose.

- Port: `9092` (TCP/JDBC)
- Persistent volume: `h2_data:/data`
- Database file is created on first API startup.
- Schema bootstrap currently remains in the API's startup initialization (`backend/app/db/schema.sql`); versioned SQL migration files are in `backend/migrations/`.

For production, replace H2 with a managed database such as PostgreSQL and move schema migration execution to a dedicated migration job. Do not expose H2's TCP port publicly.
