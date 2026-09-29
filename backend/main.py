import logging
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.database import engine, Base
import backend.models  # Ensure all SQLAlchemy models are registered
from backend.routes.auth import router as auth_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.aptitude import router as aptitude_router
from backend.routes.gd import router as gd_router
from backend.routes.interview import router as interview_router
from backend.routes.resume import router as resume_router
from backend.routes.companies import router as companies_router
from backend.routes.progress import router as progress_router
from backend.routes.simulation import router as simulation_router
from backend.routes.materials import router as materials_router
from backend.routes.jobs import router as jobs_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("placement_coach")

# Create database tables automatically
Base.metadata.create_all(bind=engine)
logger.info("Database tables verified and initialized.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Comprehensive AI Placement Preparation Platform for College Students",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler for clean error responses (no leaked stack traces)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Register API Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(aptitude_router)
app.include_router(gd_router)
app.include_router(interview_router)
app.include_router(resume_router)
app.include_router(companies_router)
app.include_router(progress_router)
app.include_router(simulation_router)
app.include_router(materials_router)
app.include_router(jobs_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Mount Frontend Static Directory for seamless local running
frontend_dir = settings.FRONTEND_DIR
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    logger.info(f"Frontend static files mounted from {frontend_dir}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
