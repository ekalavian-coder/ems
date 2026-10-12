import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.employees import router as employees_router
from app.db.database import initialize_database

log_dir = Path(os.getenv("LOG_DIR", "/app/logs"))
log_dir.mkdir(parents=True, exist_ok=True)
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
_file_handler = RotatingFileHandler(log_dir / "backend.log", maxBytes=5_000_000, backupCount=5)
_file_handler.setFormatter(_fmt)
for _name in ("", "uvicorn", "uvicorn.access", "uvicorn.error", "app"):
    _logger = logging.getLogger(_name)
    _logger.addHandler(_file_handler)
    if _logger.level == logging.NOTSET:
        _logger.setLevel(logging.INFO)

app = FastAPI(title="Employee Management API", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-User-Role"],
)

@app.on_event("startup")
def startup() -> None:
    initialize_database()

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

app.include_router(employees_router, prefix="/api")
