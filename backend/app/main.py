# main.py
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
import app.db.models
from app.routers.employees import router as employees_router
from app.routers.team_builder import router as team_builder_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup
    Base.metadata.create_all(bind=engine)
    # Ensure uploads storage exists
    Path(settings.DOCUMENT_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title="AI Team Builder API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    root_path="/api",
)

# CORS configuration matching cams
origins = [
    origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads static directory
if os.path.exists(settings.DOCUMENT_STORAGE_PATH):
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.DOCUMENT_STORAGE_PATH),
        name="uploads",
    )

# Include Routers
app.include_router(employees_router)
app.include_router(team_builder_router)

@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "AI Team Builder API",
        "version": settings.APP_VERSION,
        "llm_configured": bool(settings.GEMINI_API_KEY)
    }
