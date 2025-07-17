import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1.api import api_router
from .core.config import settings
from .core.logging import get_logger, setup_logging
from .db.base import close_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Clinical Sample Service...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    logger.info(
        f"Database URL: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'Not configured'}"
    )

    yield

    # Shutdown
    logger.info("Shutting down Clinical Sample Service...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A microservice for managing clinical samples in clinical trials",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log HTTP requests."""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__,
            },
        )
    else:
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns the current status of the application.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time(),
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    Returns basic information about the API.
    """
    return {
        "message": "Clinical Sample Service API",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_check": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    # Setup logging
    setup_logging()

    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )
