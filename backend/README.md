# FastAPI backend using H2 through JDBC

H2 is a JVM database. Python does not have a standard SQLAlchemy H2 dialect, so this sample uses `JayDeBeApi` + `JPype1` and the H2 JDBC driver. It keeps repository methods synchronous.

Download an H2 2.x jar from an approved source and place it at `backend/lib/h2.jar`. Example (verify/approve the version according to your organization):
```bash
mkdir -p lib
curl -L -o lib/h2.jar https://repo1.maven.org/maven2/com/h2database/h2/2.3.232/h2-2.3.232.jar
```
Set `H2_JAR_PATH` if the jar is elsewhere. The default database is `./data/ems`; the database is stored in files under `backend/data/`.

If JDBC/JPype cannot load the JVM, confirm `java -version`, `JAVA_HOME`, Python architecture, and that the JDBC jar exists.
