# Testing Implementation TODO List

## Current Coverage: 46.16% → Target: 90%+

### 🔴 Priority 1: API Layer Tests (Days 1-3)
**Expected Coverage Gain: +15-20%**

#### Authentication Endpoints (`tests/test_api/test_auth.py`)
 - [x] Setup test file with TestClient fixture
 - [x] POST /auth/register
  - [x] Valid registration success
  - [x] Duplicate email error (409)
  - [x] Duplicate username error (409)
  - [x] Invalid password format (422)
  - [x] Invalid email format (422)
  - [x] Missing required fields (422)
 - [x] POST /auth/login
  - [x] Valid login with token response
  - [x] Invalid credentials (401)
  - [x] Inactive user rejection (401)
  - [x] Missing fields (422)
 - [x] POST /auth/refresh
  - [x] Valid token refresh
  - [x] Expired refresh token (401)
  - [x] Invalid refresh token (401)
  - [x] Missing token (422)
 - [x] GET /auth/me
  - [x] Valid authenticated user data
  - [x] Invalid/expired token (401)
  - [x] No authorization header (401)

#### Sample Endpoints (`tests/test_api/test_samples.py`)
- [x] Setup authenticated client fixture
- [x] POST /samples
  - [x] Create sample with valid data
  - [x] Subject ID validation (422)
  - [x] Collection date validation (422)
  - [x] Tissue storage rule (422)
  - [x] Unauthenticated request (401)
- [x] GET /samples
  - [x] List user's samples
  - [x] Pagination (skip/limit)
  - [x] Filter by sample_type
  - [x] Filter by status
  - [x] Filter by date range
  - [x] Empty results
  - [x] Invalid pagination params
 - [x] GET /samples/{id}
  - [x] Get own sample
  - [x] Other user's sample (403)
  - [x] Sample not found (404)
  - [x] Invalid UUID format (422)
 - [x] PUT /samples/{id}
  - [x] Update own sample
  - [x] Partial update
  - [x] Other user's sample (403)
  - [x] Validation errors (422)
  - [x] Not found (404)
 - [x] DELETE /samples/{id}
  - [x] Delete own sample
  - [x] Other user's sample (403)
  - [x] Not found (404)
 - [x] GET /samples/statistics
  - [x] Get user statistics
  - [x] Verify data isolation
  - [x] Unauthenticated (401)
 - [x] GET /samples/subjects/{subject_id}
  - [x] Get samples by subject
  - [x] No results (empty list)
  - [x] Invalid subject format (422)

#### Dependencies (`tests/test_api/test_deps.py`)
- [x] get_db dependency
  - [x] Session creation
  - [x] Session cleanup
  - [x] Rollback on exception
- [x] get_current_user dependency
  - [x] Valid token → user
  - [x] Invalid token (401)
  - [x] User not found (401)
  - [x] Inactive user (401)
- [x] get_current_active_user
  - [x] Active user pass-through
  - [x] Inactive user rejection

### 🟡 Priority 2: Middleware & Security (Days 4-5)
**Expected Coverage Gain: +10-15%**

#### Main Application (`tests/test_main.py`)
 - [x] FastAPI app creation
 - [x] CORS middleware configuration
 - [x] Custom middleware registration
 - [x] Router inclusion
 - [x] Exception handler registration
 - [x] GET / endpoint
 - [x] GET /health endpoint
 - [x] OpenAPI schema customization

#### Logging Middleware (`tests/test_middleware/test_logging.py`)
- [x] Correlation ID generation
- [x] Request logging
  - [x] Method, path, headers
  - [x] Body content (with size limit)
  - [x] Query parameters
- [x] Response logging
  - [x] Status code
  - [x] Response time
  - [x] Response size
- [x] Error logging
  - [x] 4xx errors
  - [x] 5xx errors
  - [x] Exception details
- [x] Edge cases
  - [x] Large request bodies
  - [x] Binary content
  - [x] Streaming responses

#### Security Middleware (`tests/test_middleware/test_security.py`)
- [x] Rate limiting
  - [x] Request counting per IP
  - [x] Rate limit exceeded (429)
  - [x] Whitelist bypass
  - [x] Reset after time window
- [x] Security headers
  - [x] X-Content-Type-Options
  - [x] X-Frame-Options
  - [x] X-XSS-Protection
  - [x] CSP headers
- [x] Attack detection
  - [x] SQL injection patterns
  - [x] XSS attempts
  - [x] Path traversal
  - [x] Command injection
  - [x] LDAP injection
- [x] Request validation
  - [x] Max request size
  - [x] Suspicious patterns
  - [x] Malformed requests

### 🟢 Priority 3: Core Infrastructure (Days 6-7)
**Expected Coverage Gain: +8-10%**

#### Logging Module (`tests/test_core/test_logging.py`)
- [x] Logger setup
  - [x] JSON formatter configuration
  - [x] Log level configuration
  - [x] File handler setup
  - [x] Console handler setup
- [x] Correlation ID
  - [x] Context variable usage
  - [x] Async context propagation
  - [x] Default ID generation
- [x] Performance logging
  - [x] Timer context manager
  - [x] Database query logging
  - [x] API call logging
- [x] Error logging
  - [x] Exception formatting
  - [x] Stack trace inclusion
  - [x] Sensitive data masking

#### Exception Handling (`tests/test_core/test_exceptions.py`)
- [x] ValidationError
  - [x] to_dict() method
  - [x] HTTP response format
- [x] AuthenticationError
  - [x] WWW-Authenticate header
  - [x] Error details
- [x] AuthorizationError
  - [x] Resource access details
- [x] NotFoundError
  - [x] Resource type and ID
- [x] ConflictError
  - [x] Conflict details

### 🔵 Priority 4: Complete Coverage Gaps (Days 8-9)
**Expected Coverage Gain: +5-8%**

#### Repository Tests
- [x] UserRepository
  - [x] get_user_by_email error handling
  - [x] get_user_by_username error handling
  - [x] create_user constraint violations
  - [x] update_user transaction rollback
- [x] SampleRepository
  - [x] Complex filter combinations
  - [x] Statistics query edge cases
  - [x] Database connection errors
  - [x] Transaction isolation

#### Schema Tests
- [x] Auth schemas
  - [x] Password complexity edge cases
  - [x] Email validation edge cases
  - [x] Username format edge cases
- [x] Sample schemas
  - [x] Subject ID format variations
  - [x] Date validation boundaries
  - [x] Storage location validation
  - [x] Cross-field validation (tissue + storage)

### ⚪ Priority 5: Integration Tests (Day 10)
**Expected Coverage Gain: +3-5%**

#### End-to-End Workflows (`tests/test_integration/`)
- [x] Complete user journey
  - [x] Register new user
  - [x] Login and get token
  - [x] Create multiple samples
  - [x] Query with filters
  - [x] Update samples
  - [x] Delete samples
  - [x] Logout (token expiry)
- [x] Multi-user scenarios
  - [x] Data isolation verification
  - [ ] Concurrent operations
  - [x] Cross-user authorization
- [ ] Error recovery
  - [ ] Transaction rollback
  - [ ] Retry mechanisms
  - [ ] Graceful degradation

## Testing Utilities to Create

### Fixtures (`tests/conftest.py` additions)
- [x] `client` - TestClient instance
 - [x] `authenticated_client` - Client with auth token
 - [x] `db_session` - Test database session
 - [x] `test_data_builder` - Factory for test data

### Helpers (`tests/helpers.py`)
 - [x] Token generation utilities
 - [x] Test data factories
 - [x] Response assertion helpers
 - [x] Database state validators

## Coverage Checkpoints

- [x] After Priority 1: ~65% coverage
- [x] After Priority 2: ~75% coverage
- [x] After Priority 3: ~83% coverage
- [x] After Priority 4: ~88% coverage
- [ ] After Priority 5: 90%+ coverage

## Notes

- Run `pytest --cov=app --cov-report=html` after each phase
- Focus on business logic and security paths
- Mock external dependencies for speed
- Keep tests independent and isolated