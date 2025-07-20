# Testing Implementation TODO List

## Current Coverage: 46.16% → Target: 90%+

### 🔴 Priority 1: API Layer Tests (Days 1-3)
**Expected Coverage Gain: +15-20%**

#### Authentication Endpoints (`tests/test_api/test_auth.py`)
- [ ] Setup test file with TestClient fixture
- [ ] POST /auth/register
  - [ ] Valid registration success
  - [ ] Duplicate email error (409)
  - [ ] Duplicate username error (409)
  - [ ] Invalid password format (422)
  - [ ] Invalid email format (422)
  - [ ] Missing required fields (422)
- [ ] POST /auth/login
  - [ ] Valid login with token response
  - [ ] Invalid credentials (401)
  - [ ] Inactive user rejection (401)
  - [ ] Missing fields (422)
- [ ] POST /auth/refresh
  - [ ] Valid token refresh
  - [ ] Expired refresh token (401)
  - [ ] Invalid refresh token (401)
  - [ ] Missing token (422)
- [ ] GET /auth/me
  - [ ] Valid authenticated user data
  - [ ] Invalid/expired token (401)
  - [ ] No authorization header (401)

#### Sample Endpoints (`tests/test_api/test_samples.py`)
- [ ] Setup authenticated client fixture
- [ ] POST /samples
  - [ ] Create sample with valid data
  - [ ] Subject ID validation (422)
  - [ ] Collection date validation (422)
  - [ ] Tissue storage rule (422)
  - [ ] Unauthenticated request (401)
- [ ] GET /samples
  - [ ] List user's samples
  - [ ] Pagination (skip/limit)
  - [ ] Filter by sample_type
  - [ ] Filter by status
  - [ ] Filter by date range
  - [ ] Empty results
  - [ ] Invalid pagination params
- [ ] GET /samples/{id}
  - [ ] Get own sample
  - [ ] Other user's sample (403)
  - [ ] Sample not found (404)
  - [ ] Invalid UUID format (422)
- [ ] PUT /samples/{id}
  - [ ] Update own sample
  - [ ] Partial update
  - [ ] Other user's sample (403)
  - [ ] Validation errors (422)
  - [ ] Not found (404)
- [ ] DELETE /samples/{id}
  - [ ] Delete own sample
  - [ ] Other user's sample (403)
  - [ ] Not found (404)
- [ ] GET /samples/statistics
  - [ ] Get user statistics
  - [ ] Verify data isolation
  - [ ] Unauthenticated (401)
- [ ] GET /samples/subjects/{subject_id}
  - [ ] Get samples by subject
  - [ ] No results (empty list)
  - [ ] Invalid subject format (422)

#### Dependencies (`tests/test_api/test_deps.py`)
- [ ] get_db dependency
  - [ ] Session creation
  - [ ] Session cleanup
  - [ ] Rollback on exception
- [ ] get_current_user dependency
  - [ ] Valid token → user
  - [ ] Invalid token (401)
  - [ ] User not found (401)
  - [ ] Inactive user (401)
- [ ] get_current_active_user
  - [ ] Active user pass-through
  - [ ] Inactive user rejection

### 🟡 Priority 2: Middleware & Security (Days 4-5)
**Expected Coverage Gain: +10-15%**

#### Main Application (`tests/test_main.py`)
- [ ] FastAPI app creation
- [ ] CORS middleware configuration
- [ ] Custom middleware registration
- [ ] Router inclusion
- [ ] Exception handler registration
- [ ] GET / endpoint
- [ ] GET /health endpoint
- [ ] OpenAPI schema customization

#### Logging Middleware (`tests/test_middleware/test_logging.py`)
- [ ] Correlation ID generation
- [ ] Request logging
  - [ ] Method, path, headers
  - [ ] Body content (with size limit)
  - [ ] Query parameters
- [ ] Response logging
  - [ ] Status code
  - [ ] Response time
  - [ ] Response size
- [ ] Error logging
  - [ ] 4xx errors
  - [ ] 5xx errors
  - [ ] Exception details
- [ ] Edge cases
  - [ ] Large request bodies
  - [ ] Binary content
  - [ ] Streaming responses

#### Security Middleware (`tests/test_middleware/test_security.py`)
- [ ] Rate limiting
  - [ ] Request counting per IP
  - [ ] Rate limit exceeded (429)
  - [ ] Whitelist bypass
  - [ ] Reset after time window
- [ ] Security headers
  - [ ] X-Content-Type-Options
  - [ ] X-Frame-Options
  - [ ] X-XSS-Protection
  - [ ] CSP headers
- [ ] Attack detection
  - [ ] SQL injection patterns
  - [ ] XSS attempts
  - [ ] Path traversal
  - [ ] Command injection
  - [ ] LDAP injection
- [ ] Request validation
  - [ ] Max request size
  - [ ] Suspicious patterns
  - [ ] Malformed requests

### 🟢 Priority 3: Core Infrastructure (Days 6-7)
**Expected Coverage Gain: +8-10%**

#### Logging Module (`tests/test_core/test_logging.py`)
- [ ] Logger setup
  - [ ] JSON formatter configuration
  - [ ] Log level configuration
  - [ ] File handler setup
  - [ ] Console handler setup
- [ ] Correlation ID
  - [ ] Context variable usage
  - [ ] Async context propagation
  - [ ] Default ID generation
- [ ] Performance logging
  - [ ] Timer context manager
  - [ ] Database query logging
  - [ ] API call logging
- [ ] Error logging
  - [ ] Exception formatting
  - [ ] Stack trace inclusion
  - [ ] Sensitive data masking

#### Exception Handling (`tests/test_core/test_exceptions.py`)
- [ ] ValidationError
  - [ ] to_dict() method
  - [ ] HTTP response format
- [ ] AuthenticationError
  - [ ] WWW-Authenticate header
  - [ ] Error details
- [ ] AuthorizationError
  - [ ] Resource access details
- [ ] NotFoundError
  - [ ] Resource type and ID
- [ ] ConflictError
  - [ ] Conflict details

### 🔵 Priority 4: Complete Coverage Gaps (Days 8-9)
**Expected Coverage Gain: +5-8%**

#### Repository Tests
- [ ] UserRepository
  - [ ] get_user_by_email error handling
  - [ ] get_user_by_username error handling
  - [ ] create_user constraint violations
  - [ ] update_user transaction rollback
- [ ] SampleRepository
  - [ ] Complex filter combinations
  - [ ] Statistics query edge cases
  - [ ] Database connection errors
  - [ ] Transaction isolation

#### Schema Tests
- [ ] Auth schemas
  - [ ] Password complexity edge cases
  - [ ] Email validation edge cases
  - [ ] Username format edge cases
- [ ] Sample schemas
  - [ ] Subject ID format variations
  - [ ] Date validation boundaries
  - [ ] Storage location validation
  - [ ] Cross-field validation (tissue + storage)

### ⚪ Priority 5: Integration Tests (Day 10)
**Expected Coverage Gain: +3-5%**

#### End-to-End Workflows (`tests/test_integration/`)
- [ ] Complete user journey
  - [ ] Register new user
  - [ ] Login and get token
  - [ ] Create multiple samples
  - [ ] Query with filters
  - [ ] Update samples
  - [ ] Delete samples
  - [ ] Logout (token expiry)
- [ ] Multi-user scenarios
  - [ ] Data isolation verification
  - [ ] Concurrent operations
  - [ ] Cross-user authorization
- [ ] Error recovery
  - [ ] Transaction rollback
  - [ ] Retry mechanisms
  - [ ] Graceful degradation

## Testing Utilities to Create

### Fixtures (`tests/conftest.py` additions)
- [ ] `client` - TestClient instance
- [ ] `authenticated_client` - Client with auth token
- [ ] `db_session` - Test database session
- [ ] `test_data_builder` - Factory for test data

### Helpers (`tests/helpers.py`)
- [ ] Token generation utilities
- [ ] Test data factories
- [ ] Response assertion helpers
- [ ] Database state validators

## Coverage Checkpoints

- [ ] After Priority 1: ~65% coverage
- [ ] After Priority 2: ~75% coverage
- [ ] After Priority 3: ~83% coverage
- [ ] After Priority 4: ~88% coverage
- [ ] After Priority 5: 90%+ coverage

## Notes

- Run `pytest --cov=app --cov-report=html` after each phase
- Focus on business logic and security paths
- Mock external dependencies for speed
- Keep tests independent and isolated