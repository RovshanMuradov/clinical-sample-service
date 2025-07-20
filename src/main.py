import os
import time
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

# Import models and configuration
from models import User, Sample
from config import Settings
from api_routes import api_router
from exceptions import (
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

# Initialize settings
settings = Settings()

# Create FastAPI application optimized for Lambda
app = FastAPI(
    title="Clinical Sample Service API",
    version="1.0.0",
    description="Clinical Sample Service API for Lambda deployment",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=False,  # Always False in Lambda
)

# Fix for Swagger UI in API Gateway environment
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/Prod/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url="/Prod/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Configure security scheme for Swagger UI
security_scheme = HTTPBearer(
    scheme_name="JWT",
    description="Enter JWT token obtained from /api/v1/auth/login endpoint",
)

# Add CORS middleware with simple settings for Lambda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lambda behind API Gateway
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
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
def validation_error_handler(request: Request, exc: ValidationError):
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
def authentication_error_handler(request: Request, exc: AuthenticationError):
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
def authorization_error_handler(request: Request, exc: AuthorizationError):
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
def conflict_error_handler(request: Request, exc: ConflictError):
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
def database_error_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )

@app.exception_handler(BaseAPIException)
def base_api_exception_handler(request: Request, exc: BaseAPIException):
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

# Global exception handler
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
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
def health_check():
    """Health check endpoint for Lambda."""
    return {
        "status": "healthy",
        "service": "Clinical Sample Service",
        "version": "1.0.1",
        "timestamp": time.time(),
        "environment": "lambda",
        "database": "postgresql-ready",
    }

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {
        "message": "Clinical Sample Service API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health",
        "environment": "lambda",
    }