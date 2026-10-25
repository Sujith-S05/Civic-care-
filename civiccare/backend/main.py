import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import Base, engine
from config import settings
from routers import auth_router, complaints_router

# Create tables (for a class project; use Alembic migrations for production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CivicCare API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # allow_credentials must be False when allow_origins is "*" — browsers
    # reject the wildcard+credentials combo, which was silently breaking
    # every fetch() call from the frontend when it was on a different
    # origin/port to the API during development.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(complaints_router.router)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/citizen")
    def serve_citizen():
        return FileResponse(os.path.join(FRONTEND_DIR, "citizen_dashboard.html"))

    @app.get("/admin")
    def serve_admin():
        return FileResponse(os.path.join(FRONTEND_DIR, "admin_dashboard.html"))


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
