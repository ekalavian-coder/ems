import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_JAR = BASE_DIR / "lib" / "h2-2.3.232.jar"
JAR_PATH = Path(os.getenv("H2_JAR_PATH", str(DEFAULT_JAR))).expanduser()
DB_URL = os.getenv("H2_JDBC_URL", f"jdbc:h2:tcp://localhost:9092/./emsdb")
DB_USER = os.getenv("H2_USER", "sa")
DB_PASSWORD = os.getenv("H2_PASSWORD", "")

def get_connection():
    import jaydebeapi
    if not JAR_PATH.exists():
        raise RuntimeError(
            f"H2 JDBC jar not found at {JAR_PATH}. Place an approved H2 jar there or set H2_JAR_PATH."
        )
    return jaydebeapi.connect(
        "org.h2.Driver",
        DB_URL,
        [DB_USER, DB_PASSWORD],
        str(JAR_PATH),
    )

def initialize_database() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    statements = [s.strip() for s in schema_path.read_text(encoding="utf-8").split(";") if s.strip()]
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            for statement in statements:
                cursor.execute(statement)
        finally:
            cursor.close()
        connection.commit()
    finally:
        connection.close()
