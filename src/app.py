"""
Lambda handler for Clinical Sample Service API.
Uses Mangum to adapt FastAPI for AWS Lambda.
"""

import os
import logging

from mangum import Mangum
from main import app

# Configure logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Lambda handler using Mangum
lambda_handler = Mangum(
    app, 
    lifespan="off",  # Disable lifespan events for Lambda
    api_gateway_base_path="/Prod",  # SAM default stage
    text_mime_types=[
        "application/json",
        "application/javascript", 
        "application/xml",
        "application/vnd.api+json",
        "text/html",
        "text/plain",
        "text/css",
    ]
)

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)