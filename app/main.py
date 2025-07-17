import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1.api import api_router
from .core.config import settings
from .core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BaseAPIException,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
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
    db_info = (
        settings.database_url.split('@')[1]
        if '@' in settings.database_url
        else 'Not configured'
    )
    logger.info(f"Database URL: {db_info}")

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


# Custom exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    """Handle NotFoundError exceptions."""
    logger.warning(f"Resource not found: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle ValidationError exceptions."""
    logger.warning(f"Validation error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle AuthenticationError exceptions."""
    logger.warning(f"Authentication error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(request: Request, exc: AuthorizationError):
    """Handle AuthorizationError exceptions."""
    logger.warning(f"Authorization error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(ConflictError)
async def conflict_error_handler(request: Request, exc: ConflictError):
    """Handle ConflictError exceptions."""
    logger.warning(f"Conflict error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """Handle DatabaseError exceptions."""
    logger.error(f"Database error: {exc.message}", exc_info=True)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details if settings.debug else {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(request: Request, exc: RateLimitError):
    """Handle RateLimitError exceptions."""
    logger.warning(f"Rate limit exceeded: {exc.message}")

    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )

    # Add Retry-After header if available
    if "retry_after" in exc.details:
        response.headers["Retry-After"] = str(exc.details["retry_after"])

    return response


@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    """Handle ExternalServiceError exceptions."""
    logger.error(f"External service error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle any BaseAPIException that wasn't caught by specific handlers."""
    logger.error(f"Unhandled API exception: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


# Global exception handler for non-API exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": {
                    "exception_type": type(exc).__name__,
                    "exception_detail": str(exc),
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": {},
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )


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
