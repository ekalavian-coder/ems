import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.employees import router as employees_router
from app.db.database import initialize_database

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
