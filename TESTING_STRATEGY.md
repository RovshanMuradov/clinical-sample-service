# Clinical Sample Service Testing Strategy

## Current Test Coverage Analysis

**Current Coverage: 46.16%** (1352 statements, 698 missed)

### Existing Test Coverage
- **Service Layer**: Well-tested (AuthService ~66%, SampleService ~94%)
- **Repository Layer**: Partially tested (SampleRepository ~81%, UserRepository ~54%)
- **Schemas**: Partially tested (Sample ~76%, Auth ~65%)
- **Security Module**: Well-tested (~85%)
- **Models**: Fully tested (100%)

### Critical Gaps (0% Coverage)
1. **API Layer** (deps.py, endpoints/*.py)
2. **Main Application** (main.py)
3. **Middleware** (logging_middleware.py, security_middleware.py)
4. **Core Logging** (logging.py)

## Testing Strategy to Achieve 90%+ Coverage

### Phase 1: API Layer Tests (Critical Priority)

#### 1.1 Authentication Endpoints Tests (`tests/test_api/test_auth.py`)
```python
# Test coverage needed for app/api/v1/endpoints/auth.py (21 statements)
- POST /auth/register
  -  Valid registration
  -  Duplicate email/username
  -  Invalid password format
  -  Invalid email format
  -  Missing required fields
  
- POST /auth/login
  -  Valid login
  -  Invalid credentials
  -  Inactive user
  -  Missing fields
  
- POST /auth/refresh
  -  Valid token refresh
  -  Expired refresh token
  -  Invalid refresh token
  
- GET /auth/me
  -  Valid authenticated user
  -  Invalid/expired token
  -  No token provided
```

#### 1.2 Sample Endpoints Tests (`tests/test_api/test_samples.py`)
```python
# Test coverage needed for app/api/v1/endpoints/samples.py (40 statements)
- POST /samples
  -  Create sample with valid data
  -  Business rule violations
  -  Unauthenticated request
  -  Validation errors
  
- GET /samples
  -  List samples with pagination
  -  Filter by type/status/date
  -  Empty results
  -  Invalid pagination params
  
- GET /samples/{id}
  -  Get existing sample
  -  Access denied (other user's sample)
  -  Sample not found
  -  Invalid UUID format
  
- PUT /samples/{id}
  -  Update own sample
  -  Authorization error
  -  Validation errors
  -  Not found
  
- DELETE /samples/{id}
  -  Delete own sample
  -  Authorization error
  -  Not found
  
- GET /samples/statistics
  -  Get user statistics
  -  Unauthenticated request
  
- GET /samples/subjects/{subject_id}
  -  Get samples by subject
  -  No results
  -  Invalid subject format
```

#### 1.3 Dependencies Tests (`tests/test_api/test_deps.py`)
```python
# Test coverage needed for app/api/deps.py (34 statements)
- get_db dependency
  -  Session creation/cleanup
  -  Transaction rollback on error
  
- get_current_user dependency
  -  Valid token extraction
  -  Invalid token handling
  -  User not found
  -  Inactive user
  
- get_current_active_user dependency
  -  Active user validation
  -  Inactive user rejection
```

### Phase 2: Application & Middleware Tests

#### 2.1 Main Application Tests (`tests/test_main.py`)
```python
# Test coverage needed for app/main.py (98 statements)
- Application startup
  -  FastAPI app initialization
  -  CORS configuration
  -  Middleware registration
  -  Router inclusion
  -  Exception handlers
  
- Health check endpoint
  -  GET /health
  -  GET /
  
- OpenAPI configuration
  -  Custom OpenAPI schema
  -  API documentation
```

#### 2.2 Logging Middleware Tests (`tests/test_middleware/test_logging.py`)
```python
# Test coverage needed for app/middleware/logging_middleware.py (89 statements)
- Request logging
  -  Correlation ID generation
  -  Request details capture
  -  Response logging
  -  Error logging
  -  Performance metrics
  
- Edge cases
  -  Large request bodies
  -  Binary content
  -  Streaming responses
```

#### 2.3 Security Middleware Tests (`tests/test_middleware/test_security.py`)
```python
# Test coverage needed for app/middleware/security_middleware.py (141 statements)
- Rate limiting
  -  Request counting
  -  Rate limit enforcement
  -  IP-based tracking
  -  Whitelist handling
  
- Security headers
  -  XSS protection
  -  Content type options
  -  Frame options
  -  CSP headers
  
- Attack detection
  -  SQL injection patterns
  -  XSS patterns
  -  Path traversal
  -  Command injection
  
- Request validation
  -  Size limits
  -  Suspicious patterns
  -  Malformed requests
```

### Phase 3: Core Infrastructure Tests

#### 3.1 Logging Module Tests (`tests/test_core/test_logging.py`)
```python
# Test coverage needed for app/core/logging.py (117 statements)
- Logger configuration
  -  JSON formatter
  -  Log levels
  -  File rotation
  -  Console output
  
- Correlation ID handling
  -  ID generation
  -  Context propagation
  -  Async context
  
- Performance logging
  -  Request timing
  -  Database query logging
  -  Error tracking
```

#### 3.2 Exception Handling Tests (`tests/test_core/test_exceptions.py`)
```python
# Additional coverage for app/core/exceptions.py (missing ~40%)
- Custom exception behavior
  -  HTTP response generation
  -  Error detail formatting
  -  Status code mapping
  -  Logging integration
```

### Phase 4: Repository & Schema Completion

#### 4.1 Repository Tests (`tests/test_repositories/`)
```python
# Additional coverage needed:
- UserRepository (~46% missing)
  -  Error handling paths
  -  Transaction rollback
  -  Constraint violations
  
- SampleRepository (~19% missing)
  -  Complex query scenarios
  -  Edge cases in filtering
  -  Database errors
```

#### 4.2 Schema Validation Tests (`tests/test_schemas/`)
```python
# Additional coverage needed:
- Auth schemas (~35% missing)
  -  All validator edge cases
  -  Error message formatting
  
- Sample schemas (~24% missing)
  -  Complex validation scenarios
  -  Cross-field validation
```

### Phase 5: Integration Tests

#### 5.1 End-to-End Workflows (`tests/test_integration/`)
```python
- Complete user journey
  -  Register ’ Login ’ Create samples ’ Query ’ Update ’ Delete
  -  Multi-user scenarios
  -  Token refresh flow
  -  Error recovery
  
- Database transactions
  -  Rollback scenarios
  -  Concurrent access
  -  Data consistency
```

## Implementation Plan

### Priority 1: API Layer (Days 1-3)
- Create `tests/test_api/` directory
- Implement all endpoint tests using FastAPI TestClient
- Focus on authentication flow and sample CRUD
- **Expected coverage gain: +15-20%**

### Priority 2: Middleware & Security (Days 4-5)
- Create `tests/test_middleware/` directory
- Test security patterns and rate limiting
- Validate logging behavior
- **Expected coverage gain: +10-15%**

### Priority 3: Core Infrastructure (Days 6-7)
- Complete logging and exception tests
- Test database session management
- **Expected coverage gain: +8-10%**

### Priority 4: Complete Existing Gaps (Days 8-9)
- Fill repository test gaps
- Complete schema validation tests
- **Expected coverage gain: +5-8%**

### Priority 5: Integration Tests (Days 10)
- End-to-end scenarios
- Performance testing
- **Expected coverage gain: +3-5%**

## Test Implementation Guidelines

### 1. Use Consistent Test Structure
```python
class TestFeatureName:
    """Test {feature} functionality."""
    
    async def test_happy_path(self):
        """Test successful {operation}."""
        # Arrange
        # Act
        # Assert
    
    async def test_validation_errors(self):
        """Test {operation} with invalid data."""
        # Test each validation rule
    
    async def test_authorization(self):
        """Test {operation} authorization."""
        # Test access control
    
    async def test_error_handling(self):
        """Test {operation} error scenarios."""
        # Test various failure modes
```

### 2. Use Fixtures Effectively
```python
@pytest.fixture
async def authenticated_client(client: TestClient, test_user: User):
    """Client with valid authentication token."""
    token = create_access_token({"sub": str(test_user.id)})
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### 3. Test Data Builders
```python
def build_sample_data(**overrides) -> dict:
    """Build valid sample data with overrides."""
    defaults = {
        "sample_type": "blood",
        "subject_id": "P001",
        "collection_date": str(date.today()),
        "storage_location": "freezer-1-rowA"
    }
    return {**defaults, **overrides}
```

### 4. Mock External Dependencies
```python
@patch("app.core.logging.logger")
async def test_with_mocked_logger(mock_logger):
    """Test with mocked logger to verify logging calls."""
    # Test implementation
    mock_logger.info.assert_called_with(...)
```

## Success Metrics

1. **Coverage Target**: 90%+ overall, 95%+ for critical paths
2. **Test Execution Time**: < 30 seconds for unit tests
3. **Test Reliability**: 0% flaky tests
4. **Documentation**: Every test has clear docstring

## Testing Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Speed**: Mock heavy operations (DB, external APIs)
4. **Coverage**: Focus on behavior, not just lines
5. **Maintenance**: Keep tests simple and focused

## Next Steps

1. Create test directory structure
2. Set up additional test fixtures
3. Implement Priority 1 tests (API layer)
4. Run coverage reports after each phase
5. Adjust strategy based on coverage gaps