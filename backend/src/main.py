"""
FastAPI main application entry point for KVTM Auto
Android device automation backend
"""

from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .api.devices import router as devices_router
from .api.execute import router as execute_router
from .api.scripts import router as scripts_router
from .libs.time_provider import GMT_PLUS_7
from .service.executor import executor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Setup logging
    log_path = Path("src/logs/application.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    logger.info("Starting KVTM Auto Backend...")
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down KVTM Auto Backend...")
    
    # Stop all running device processes
    logger.info("Stopping all device processes...")
    result = executor.shutdown_all()
    logger.info(f"Shutdown result: {result}")
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="KVTM Auto API",
    description="Android device automation backend with ADB integration",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "error": str(exc)}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "kvtm-auto-backend", "version": "1.0.0"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "KVTM Auto Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "devices": "/api/devices",
            "scripts": "/api/scripts",
            "execute": "/api/execute",
        },
    }


# Include API routers
app.include_router(devices_router, prefix="/api/devices", tags=["devices"])
app.include_router(scripts_router, prefix="/api/scripts", tags=["scripts"])
app.include_router(execute_router, prefix="/api/execute", tags=["execute"])


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
