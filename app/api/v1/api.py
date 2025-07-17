from fastapi import APIRouter

from .endpoints import auth, samples

# Create main API router
api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include sample routes
api_router.include_router(samples.router, prefix="/samples", tags=["Samples"])


# API status endpoint
@api_router.get("/status", tags=["API Status"])
async def api_status():
    """
    API status endpoint.
    Returns the current status of the API.
    """
    return {
        "status": "online",
        "version": "1.0.0",
        "endpoints": {"auth": "/api/v1/auth", "samples": "/api/v1/samples"},
    }
