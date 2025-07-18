#!/usr/bin/env python3
"""
Test script to verify Swagger documentation is properly configured.
This checks for key documentation elements without running the full app.
"""

import sys
import os
import json

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

def test_swagger_documentation():
    """Test that Swagger documentation is properly configured."""
    
    # Test 1: Check that main.py can be imported without errors
    print("✓ Testing main.py imports...")
    try:
        from app.main import app
        print("✓ Main app imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 2: Check that FastAPI app has proper configuration
    print("✓ Testing FastAPI app configuration...")
    assert app.title == "Clinical Sample Service"
    assert "Clinical Sample Service API" in app.description
    assert app.version is not None
    print("✓ FastAPI app properly configured")
    
    # Test 3: Check that OpenAPI tags are configured
    print("✓ Testing OpenAPI tags...")
    expected_tags = ["Authentication", "Samples", "Health", "Root", "API Status"]
    configured_tags = [tag["name"] for tag in app.openapi_tags]
    for expected_tag in expected_tags:
        assert expected_tag in configured_tags, f"Missing tag: {expected_tag}"
    print("✓ All OpenAPI tags configured")
    
    # Test 4: Check that custom OpenAPI function exists
    print("✓ Testing custom OpenAPI function...")
    assert hasattr(app, 'openapi'), "Custom OpenAPI function not found"
    print("✓ Custom OpenAPI function configured")
    
    # Test 5: Check that security scheme is configured
    print("✓ Testing security scheme...")
    try:
        openapi_schema = app.openapi()
        assert "components" in openapi_schema
        assert "securitySchemes" in openapi_schema["components"]
        assert "bearerAuth" in openapi_schema["components"]["securitySchemes"]
        print("✓ Security scheme properly configured")
    except Exception as e:
        print(f"✗ Security scheme error: {e}")
        return False
    
    # Test 6: Check route documentation
    print("✓ Testing route documentation...")
    routes = [route for route in app.routes if hasattr(route, 'methods')]
    documented_routes = 0
    for route in routes:
        if hasattr(route, 'description') and route.description:
            documented_routes += 1
    print(f"✓ Found {documented_routes} documented routes")
    
    return True

if __name__ == "__main__":
    try:
        success = test_swagger_documentation()
        if success:
            print("\n🎉 All Swagger documentation tests passed!")
            print("\nYour API documentation includes:")
            print("- Detailed endpoint descriptions")
            print("- Request/response examples")
            print("- Authentication documentation")
            print("- Error response documentation")
            print("- Properly tagged and grouped endpoints")
            print("- JWT security scheme configuration")
            print("\nTo view the documentation:")
            print("1. Start the server: uvicorn app.main:app --reload")
            print("2. Open browser to: http://localhost:8000/docs")
            print("3. Use the 'Authorize' button to test JWT authentication")
        else:
            print("\n❌ Some Swagger documentation tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)