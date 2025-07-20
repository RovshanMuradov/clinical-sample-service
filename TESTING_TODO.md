# Testing Implementation Plan for Clinical Sample Service

**Current Status:** 23% coverage (Need ≥70%) | 41 unit tests exist

## Priority 1: Critical (For Production) - Target: +40% coverage

### 1.1 API Integration Tests
**Location:** `tests/test_api_integration.py`
**Goal:** Test all REST endpoints through FastAPI TestClient

**Create file with these exact test functions:**

```python
# Test Authentication Endpoints
def test_register_user_success()
def test_register_duplicate_email_fails()
def test_login_valid_credentials()
def test_login_invalid_credentials()
def test_refresh_token_valid()
def test_refresh_token_expired()

# Test Sample CRUD Endpoints  
def test_create_sample_authenticated()
def test_create_sample_unauthenticated_fails()
def test_get_samples_list_authenticated()
def test_get_samples_with_filtering()
def test_get_sample_by_id_success()
def test_get_sample_by_id_not_found()
def test_update_sample_authenticated()
def test_update_sample_unauthorized_fails()
def test_delete_sample_authenticated()
def test_delete_sample_unauthorized_fails()

# Test Statistics Endpoints
def test_get_sample_statistics_authenticated()
def test_get_samples_by_subject_authenticated()

# Test Health Check
def test_health_check_endpoint()
```

**Implementation Requirements:**
- Use `httpx.AsyncClient` with FastAPI app
- Test HTTP status codes (200, 201, 400, 401, 403, 404)
- Verify response JSON structure matches schemas
- Test data isolation between users
- Include pagination testing

### 1.2 FastAPI Application Tests
**Location:** `tests/test_main_app.py`
**Goal:** Test app/main.py initialization and middleware

**Create file with these exact test functions:**

```python
def test_fastapi_app_creation()
def test_cors_middleware_configured()
def test_exception_handlers_registered()
def test_api_router_included()
def test_startup_event_handlers()
```

**Implementation Requirements:**
- Test FastAPI app object creation
- Verify all middleware is attached
- Test exception handler registration
- Confirm API routes are properly included

### 1.3 Middleware Tests
**Location:** `tests/test_middleware.py`
**Goal:** Test logging, security, and performance middleware

**Create file with these exact test functions:**

```python
# LoggingMiddleware Tests
def test_logging_middleware_adds_correlation_id()
def test_logging_middleware_logs_requests()
def test_logging_middleware_logs_responses()

# SecurityLoggingMiddleware Tests  
def test_security_middleware_detects_sql_injection()
def test_security_middleware_checks_headers()
def test_security_middleware_validates_user_agent()

# PerformanceLoggingMiddleware Tests
def test_performance_middleware_measures_time()
def test_performance_middleware_logs_slow_requests()
```

**Implementation Requirements:**
- Mock logging calls and verify log messages
- Test middleware ordering and execution
- Verify correlation IDs are generated
- Test security detection patterns

## Priority 2: Important - Target: +15% coverage

### 2.1 Core Security Tests
**Location:** `tests/test_core_security.py`
**Goal:** Test app/core/security.py JWT functions

**Create file with these exact test functions:**

```python
def test_create_access_token()
def test_verify_token_valid()
def test_verify_token_expired()
def test_verify_token_invalid_signature()
def test_decode_token_success()
def test_decode_token_malformed()
def test_get_password_hash()
def test_verify_password_correct()
def test_verify_password_incorrect()
```

### 2.2 Exception Handler Tests
**Location:** `tests/test_exception_handlers.py`
**Goal:** Test global exception handling in main.py

**Create file with these exact test functions:**

```python
def test_not_found_error_handler()
def test_validation_error_handler()  
def test_authentication_error_handler()
def test_authorization_error_handler()
def test_database_error_handler()
def test_generic_exception_handler()
```

### 2.3 Dependency Injection Tests
**Location:** `tests/test_api_deps.py`
**Goal:** Test app/api/deps.py dependencies

**Create file with these exact test functions:**

```python
def test_get_db_dependency()
def test_get_current_user_valid_token()
def test_get_current_user_invalid_token()
def test_get_current_user_expired_token()
def test_get_current_user_missing_token()
```

## Priority 3: Desirable - Target: +10% coverage

### 3.1 Repository Layer Tests
**Location:** `tests/test_repositories_extended.py`
**Goal:** Full coverage of repository methods

**Test missing repository methods:**
- UserRepository edge cases
- SampleRepository complex queries
- Error handling in repositories

### 3.2 Performance Tests
**Location:** `tests/test_performance.py`
**Goal:** Test response times and concurrent requests

**Create file with these exact test functions:**

```python
def test_api_response_time_under_threshold()
def test_concurrent_sample_creation()
def test_database_query_performance()
```

## Implementation Instructions for AI

### Setup Requirements
1. **Test Database:** Use existing SQLite in-memory from conftest.py
2. **TestClient:** Import from `fastapi.testclient` 
3. **Fixtures:** Use existing fixtures from `conftest.py`
4. **Async Tests:** Use `pytest.mark.asyncio` for async functions

### Code Standards
1. **HTTP Status Testing:** Always verify exact status codes
2. **JSON Response Testing:** Validate response structure matches Pydantic schemas
3. **Authentication Testing:** Use existing token creation utilities
4. **Data Isolation:** Every test must verify user can only access own data
5. **Error Testing:** Test both success and failure scenarios

### Coverage Goals
- **After Priority 1:** 63% coverage (23% + 40%)
- **After Priority 2:** 78% coverage (63% + 15%)
- **After Priority 3:** 88% coverage (78% + 10%)

### File Structure
```
tests/
├── conftest.py (exists)
├── test_main.py (exists - basic tests)
├── test_auth_service.py (exists)
├── test_sample_service.py (exists) 
├── test_user_repository.py (exists)
├── test_sample_repository.py (exists)
├── test_api_integration.py (CREATE - Priority 1)
├── test_main_app.py (CREATE - Priority 1)
├── test_middleware.py (CREATE - Priority 1)
├── test_core_security.py (CREATE - Priority 2)
├── test_exception_handlers.py (CREATE - Priority 2)
├── test_api_deps.py (CREATE - Priority 2)
├── test_repositories_extended.py (CREATE - Priority 3)
└── test_performance.py (CREATE - Priority 3)
```

## Execution Order
1. Start with Priority 1 tests (biggest coverage impact)
2. Run `pytest --cov=app --cov-report=term` after each file
3. Verify coverage increases as expected
4. Move to Priority 2 only after Priority 1 reaches target
5. **Target: 70%+ coverage minimum for production readiness**

## Critical Testing Requirements
- **Data Isolation:** Every API test must verify users see only their data
- **Authentication:** Test both authenticated and unauthenticated scenarios
- **HTTP Status Codes:** Verify exact status codes (200, 201, 400, 401, 403, 404, 500)
- **Error Responses:** Test error message format matches ErrorResponse schema
- **Pagination:** Test skip/limit parameters work correctly
- **Filtering:** Test all sample filtering parameters

## Success Criteria
✅ 70%+ code coverage
✅ All API endpoints tested
✅ All middleware tested  
✅ Data isolation verified
✅ Authentication/Authorization tested
✅ Error handling tested