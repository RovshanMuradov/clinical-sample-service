# TODO: Stage 1 - Basic Setup and Infrastructure

## 1. Environment and Configuration Setup

### 1.1 Creating .env file
- [x] Create .env file with the following variables:
  ```
  DATABASE_URL=postgresql+asyncpg://user:password@localhost/clinical_samples_db
  SECRET_KEY=your-secret-key-here
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  DEBUG=True
  LOG_LEVEL=INFO
  ```

### 1.2 Implementing core/config.py
- [x] Create Settings class using pydantic-settings
- [x] Add environment variables validation
- [x] Configure loading from .env file
- [x] Include the following settings:
  - Database connection
  - JWT parameters
  - Application settings (name, version)
  - CORS settings

### 1.3 Setting up logging in core/logging.py
- [x] Create centralized logging configuration
- [x] Configure log formatting
- [x] Add log file rotation
- [x] Configure logging levels from configuration

## 2. Database Setup

### 2.1 Creating basic database connection
- [x] Create app/db/base.py file ✓ (app/db/ folder created)
- [x] Configure SQLAlchemy engine
- [x] Create SessionLocal and Base
- [x] Create get_db function for dependency injection

### 2.2 Models initialization
- [x] Create app/db/__init__.py
- [x] Import all models for Alembic
- [x] Create basic structure for models

### 2.3 Alembic setup
- [x] Initialize Alembic: `alembic init alembic`
- [x] Configure alembic.ini with correct DATABASE_URL
- [x] Update alembic/env.py to work with our models
- [x] Create first migration ✓ (completed in Stage 2)

## 3. Docker Environment

### 3.1 Creating Dockerfile
- [x] Create multi-stage Dockerfile
- [x] Configure base Python 3.11 image (used in project)
- [x] Install dependencies
- [x] Configure working directory
- [x] Add healthcheck
- [x] Configure startup through uvicorn

### 3.2 Setting up docker-compose.yml
- [x] Create service for application
- [x] Create service for PostgreSQL
- [x] Configure volumes for DB
- [x] Configure network between services
- [x] Add environment variables
- [x] Configure ports

### 3.3 Creating helper scripts
- [x] Create script for DB initialization
- [x] Create .dockerignore file

## 4. Basic Application Structure

### 4.1 Setting up main.py
- [x] Create FastAPI application
- [x] Configure CORS
- [x] Add middleware for logging
- [x] Configure exception handling
- [x] Add health check endpoint

### 4.2 Creating basic dependencies
- [x] Create app/api/deps.py
- [x] Add dependency for getting DB session
- [x] Prepare structure for future auth dependencies

## Stage Completion Criteria
- [x] Application starts locally via uvicorn
- [x] Application starts via docker-compose
- [x] Database connects successfully
- [x] Logging works correctly
- [x] Health check endpoint returns 200 OK
- [x] Configuration loads from .env file
- [x] Alembic ready to create migrations

---

# TODO: Stage 2 - Data Models and Database

## 1. Creating SQLAlchemy Models

### 1.1 User model for authentication
- [x] Create User model in app/models/user.py
- [x] Add fields: id, username, email, hashed_password, is_active, created_at, updated_at
- [x] Configure indexes for email and username (unique)
- [x] Add relationships if necessary
- [x] Import model in app/models/__init__.py

### 1.2 Sample model for clinical samples  
- [x] Create Sample model in app/models/sample.py
- [x] Add fields: id, sample_id (UUID), sample_type, subject_id, collection_date, status, storage_location, created_at, updated_at
- [x] Configure enum for sample_type (blood, saliva, tissue)
- [x] Configure enum for status (collected, processing, archived)
- [x] Add validation and constraints
- [x] Import model in app/models/__init__.py

## 2. Creating Pydantic Schemas

### 2.1 Authentication schemas
- [x] Create UserBase, UserCreate, UserUpdate, UserResponse in app/schemas/auth.py
- [x] Add UserLogin schema for login
- [x] Add Token, TokenData schemas for JWT
- [x] Configure email and password validation
- [x] Import schemas in app/schemas/__init__.py

### 2.2 Sample schemas
- [x] Create SampleBase, SampleCreate, SampleUpdate, SampleResponse in app/schemas/sample.py
- [x] Add filtering schemas: SampleFilter
- [x] Configure validation for types and statuses
- [x] Add date validation
- [x] Import schemas in app/schemas/__init__.py

## 3. Creating and Applying Database Migrations

### 3.1 Creating first migration
- [x] Run: `make migrate-create MESSAGE="Create users and samples tables"`
- [x] Check generated migration in alembic/versions/
- [x] Edit migration if necessary
- [x] Apply migration: `make migrate-up`

### 3.2 Database verification
- [x] Connect to DB and check created tables
- [x] Check indexes and constraints
- [x] Test rollback: `make migrate-down`

## Stage 2 Completion Criteria
- [x] All SQLAlchemy models created and working
- [x] All Pydantic schemas created with validation
- [x] Database created with correct tables
- [x] Migrations work correctly (up/down)
- [x] Can create/read records through SQLAlchemy

---

# TODO: Stage 3 - Authentication and Security

## 1. Implementing JWT Authentication

### 1.1 Creating security functions
- [x] Implement create_access_token() in app/core/security.py
- [x] Implement verify_token() for JWT verification
- [x] Implement get_password_hash() for password hashing
- [x] Implement verify_password() for password verification
- [x] Add decode_token() function to get data from token

### 1.2 Setting up JWT parameters
- [x] Use settings from config.py (SECRET_KEY, ALGORITHM, EXPIRE_MINUTES)
- [x] Add expired token handling
- [x] Add invalid token handling

## 2. Creating Authentication Endpoints

### 2.1 User registration
- [x] Implement POST /api/v1/auth/register in app/api/v1/endpoints/auth.py
- [x] Add email/username uniqueness validation
- [x] Hash password during registration
- [x] Return created user (without password)

### 2.2 System login
- [x] Implement POST /api/v1/auth/login 
- [x] Check user credentials
- [x] Create and return JWT token
- [x] Handle invalid credentials

### 2.3 Token refresh
- [x] Implement POST /api/v1/auth/refresh
- [x] Check valid token
- [x] Create new token

## 3. Creating Dependencies for Route Protection

### 3.1 Updating app/api/deps.py
- [x] Update get_current_user() for real JWT verification
- [x] Add user retrieval from DB by token
- [x] Handle authorization errors (401, 403)
- [x] Remove placeholder logic

### 3.2 Creating user repository
- [x] Create UserRepository in app/repositories/user_repository.py
- [x] Implement get_user_by_email()
- [x] Implement get_user_by_id()
- [x] Implement create_user()
- [x] Implement update_user()

### 3.3 Creating authentication service
- [x] Create AuthService in app/services/auth_service.py
- [x] Implement register_user()
- [x] Implement authenticate_user()
- [x] Implement get_current_user_by_token()

## 4. Integrating Authentication with Sample Endpoints

### 4.1 Updating Sample endpoints
- [x] Add real authentication to Sample endpoints in app/api/v1/endpoints/samples.py
- [x] Remove placeholder logic  
- [x] Link samples with users

## Stage 3 Completion Criteria
- [x] JWT authentication fully works
- [x] Users can register and login
- [x] Tokens are created and verified correctly
- [x] Protected endpoints require valid token
- [x] All auth endpoints return proper errors
- [x] Passwords are hashed securely

---

# TODO: Stage 4 - Core Business Logic

## 1. Implementing Repositories

### 1.1 SampleRepository for database operations
- [x] Create SampleRepository in app/repositories/sample_repository.py
- [x] Implement create_sample()
- [x] Implement get_sample_by_id()
- [x] Implement get_samples_with_filters()
- [x] Implement update_sample()
- [x] Implement delete_sample()
- [x] Add methods for record counting (count)

## 2. Implementing Service Layer

### 2.1 SampleService for business logic
- [x] Create SampleService in app/services/sample_service.py
- [x] Implement create_sample() with validation
- [x] Implement get_sample_by_id() with permission checks
- [x] Implement get_samples() with filtering and pagination
- [x] Implement update_sample() with validation
- [x] Implement delete_sample() with permission checks
- [x] Add business rules for Sample

## 3. Creating API Endpoints for Samples

### 3.1 Implementing real CRUD endpoints
- [x] Replace placeholder logic in app/api/v1/endpoints/samples.py
- [x] Implement POST /samples - creating new sample
- [x] Implement GET /samples - getting all samples
- [x] Implement GET /samples/{id} - getting specific sample
- [x] Implement PUT /samples/{id} - updating sample
- [x] Implement DELETE /samples/{id} - deleting sample

### 3.2 Integration with services and repositories
- [x] Connect SampleService to endpoints
- [x] Add dependency injection for services
- [x] Configure proper HTTP statuses
- [x] Add proper error handling

## 4. Implementing Sample Filtering (mandatory from requirements)

### 4.1 Extended filtering for GET /samples
- [x] Add query parameters for filtering in schemas
- [x] Implement filtering by status (collected, processing, archived)
- [x] Implement filtering by type (blood, saliva, tissue)
- [x] Implement filtering by subject_id
- [x] Implement filtering by collection date (from/to)
- [x] Implement combined filtering
- [x] Add filter parameter validation
- [x] Add pagination (skip, limit)

## 5. Linking Samples with Users

### 5.1 Adding user_id field to Sample model
- [x] Update Sample model with user_id field
- [x] Add Foreign Key to users table
- [x] Create migration for adding user_id field
- [x] Apply migration
- [x] Update repository for user_id filtering
- [x] Update service for access permission checks
- [x] Add data isolation (users see only their samples)

## 6. Additional Improvements

### 6.1 Additional endpoints
- [x] Implement GET /samples/subject/{subject_id} - get samples by subject ID
- [x] Implement GET /samples/stats/overview - sample statistics

### 6.2 Completing unfinished tasks from Stage 3
- [x] Complete implementation of POST /api/v1/auth/refresh
- [x] Add full JWT token validation in refresh endpoint

## Stage 4 Completion Criteria
- [x] All CRUD operations fully functional
- [x] Filtering works for all parameters
- [x] Service layer contains business logic
- [x] Repository abstracts DB operations
- [x] API returns correct HTTP statuses
- [x] Samples linked with users (data isolation)
- [x] Authorization works at data level

## 7. Fixing Critical Security Issues

### 7.1 Discovering and fixing data isolation issue in statistics
- [x] **CRITICAL**: Identified issue - statistics showed data from all users
- [x] Updated get_samples_by_status method to support user_id filtering
- [x] Added get_samples_by_type method with user_id filtering
- [x] Fixed get_sample_statistics method for correct data isolation
- [x] Implemented full by_type statistics (was empty)

### 7.2 Testing fixes
- [x] Tested statistics with multiple users
- [x] Verified data consistency (totals match)
- [x] Tested edge cases (empty data, new users)
- [x] Confirmed complete data isolation between users

🔒 **SECURITY RESTORED** - Data isolation now works correctly in all endpoints

---

# TODO: Stage 5 - Error Handling and Validation

## 1. Creating Custom Exceptions

### 1.1 Defining application exceptions
- [x] Create app/core/exceptions.py
- [x] Add NotFoundError for resources not found
- [x] Add ValidationError for validation errors
- [x] Add AuthenticationError for authentication errors
- [x] Add AuthorizationError for authorization errors
- [x] Add DatabaseError for DB errors

## 2. Global Error Handling

### 2.1 Exception handlers
- [x] Update global exception handlers in app/main.py
- [x] Add handler for ValidationError -> 400
- [x] Add handler for NotFoundError -> 404
- [x] Add handler for AuthenticationError -> 401
- [x] Add handler for AuthorizationError -> 403
- [x] Add handler for DatabaseError -> 500

### 2.2 Standardizing error responses
- [x] Create ErrorResponse schema
- [x] Standardize JSON error format
- [x] Add error codes and messages
- [ ] Error localization (optional)

## 3. Input Data Validation

### 3.1 Extended Pydantic validation
- [x] Add custom validators in schemas
- [x] Business rules validation in schemas
- [x] Cross-field dependencies validation
- [x] Add meaningful error messages

## 4. Error and Operations Logging

### 4.1 Structured logging
- [x] Update logging in app/core/logging.py
- [x] Add correlation IDs for tracing
- [x] Log all API requests/responses
- [x] Log errors with context
- [x] Configure different logging levels

## 5. Security Hardening (critical for medical data)

### 5.1 Additional API protection
- [x] Add rate limiting for API endpoints (DDoS protection)
- [x] Implement request timeout for all endpoints
- [x] Add CORS settings for production
- [x] Content-Type headers validation

### 5.2 Input Security & Validation
- [x] Validate all input data against injection attacks
- [x] Check for SQL injection (through ORM protection)
- [x] Input sanitization for all user inputs
- [ ] File upload validation (not applicable - no file uploads)
- [x] Payload size checks

### 5.3 Secrets & Data Protection
- [x] Audit secrets management (verify tokens/passwords are not logged)
- [x] Ensure sensitive data is not returned in API responses
- [x] Verify DEBUG=False in production
- [x] Validate data access permissions at all levels
- [x] Add security headers (X-Content-Type-Options, etc.)

## Stage 5 Completion Criteria
- [x] All errors handled gracefully
- [x] Clients receive clear error messages
- [x] All operations logged with context
- [x] Validation works at all levels

## Additional improvements completed beyond the plan:

### 6.1 Middleware for logging and security
- [x] Created LoggingMiddleware for request correlation
- [x] Created SecurityLoggingMiddleware for attack monitoring
- [x] Created PerformanceLoggingMiddleware for performance tracking
- [x] Integrated middleware into main application

### 6.2 Extended schema validation
- [x] Subject ID validation (format P001, S123)
- [x] Date validation (not in future, not older than 10 years)
- [x] Storage location validation (format freezer-X-rowY)
- [x] Business rules (tissue samples must be in freezer)
- [x] Password validation (special chars, weak passwords, similarity to username)
- [x] Email domain validation for clinical data
- [x] Username validation (format, reserved words)

### 6.3 Security improvements
- [x] Sensitive data filtering in logs
- [x] Suspicious request detection (SQL injection patterns)
- [x] Header size checks (DoS protection)
- [x] Suspicious User-Agent detection
- [x] All security events logging

### 6.5 ✅ COMPLETED (successfully implemented):
- [x] Rate limiting for API endpoints
- [x] Request timeout for all endpoints
- [x] Advanced CORS settings for production
- [x] Content-Type headers validation
- [x] Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- [x] Full payload size checking (not just headers)

### 6.4 Testing and code quality
- [x] Fixed all MyPy type checking errors
- [x] Fixed all flake8 linting errors
- [x] Applied black + isort formatting
- [x] Tested in production through Docker
- [x] Verified all validations work in real environment

---

## Stage 6 — Testing (Focused Approach)

**🎯 Goal:** Cover 80% of critical risks with minimal test set (~15–20 instead of 50+).

---

### 1. Test Environment Setup

- [x] Update `pyproject.toml` with pytest settings  
- [x] Create `conftest.py` with fixtures  
- [x] Set up test DB (SQLite in-memory)  
- [x] Create `test_main.py` for basic smoke tests  
- [x] Configure coverage reports  

---

### 2. Priority 1 — Critical Security and Data Isolation

#### Data Isolation

- [x] `test_user_can_only_see_own_samples()`  
- [x] `test_user_cannot_access_other_user_samples()`  
- [x] `test_statistics_only_show_user_data()`  
- [x] `test_filtering_respects_user_boundaries()`  
- [x] `test_subject_search_isolated_by_user()`  

#### Authentication

- [x] `test_password_hashing_and_verification()`  
- [x] `test_jwt_token_creation_and_validation()`  
- [x] `test_expired_token_rejection()`  
- [x] `test_invalid_token_rejection()`  

#### Authorization

- [x] `test_cannot_update_other_user_sample()`  
- [x] `test_cannot_delete_other_user_sample()`  
- [x] `test_cannot_view_other_user_sample()`  
- [x] `test_sample_creation_assigns_correct_user()`  

---

### 3. Priority 2 — Basic Functionality

#### Registration and login logic

- [x] `test_duplicate_email_registration_blocked()`  
- [x] `test_duplicate_username_registration_blocked()`  
- [x] `test_login_with_wrong_password_fails()`  
- [x] `test_inactive_user_cannot_login()`  

#### CRUD for samples

- [x] `test_create_sample_with_valid_data()`  
- [x] `test_update_sample_fields()`  
- [x] `test_update_preserves_user_isolation()`  
- [x] `test_delete_existing_sample()`  
- [x] `test_get_sample_by_id()`  
- [x] `test_sample_not_found_error()`  

---

### 4. Priority 3 — Edge Cases and Additional Checks

- [x] `test_pagination_parameters_handling()`  
- [x] `test_invalid_uuid_handling()`  

---

## Current Status

- **Total unit tests:** 41 ✅  
- **Code coverage:** 23% (need ≥ 70%)  
- **Critical risks (Data Isolation, Auth, Authorization):** 95% covered ✅  
- **API endpoints:** 0% ❌  
- **Middleware:** 0% ❌  
- **Integration tests:** missing ❌  

---

## Improvement Plan

1. 🔴 **Priority 1 (for production):**  
   - [ ] Add integration tests for all API endpoints  
   - [ ] Cover `app/main.py` with tests (FastAPI application)  
   - [ ] Test all middleware (logging, security)  

2. 🟡 **Priority 2 (important):**  
   - [ ] Tests for `app/core/security.py` (JWT functions)  
   - [ ] Tests for exception handlers  
   - [ ] Check dependency injection (`app/api/deps.py`)  

3. 🟢 **Priority 3 (desirable):**  
   - [ ] Full repository layer coverage  
   - [ ] Performance tests  
   - [ ] E2E tests through TestClient  

---

# TODO: Stage 7 - Documentation and Finalization

## 1. Creating Detailed README.md (HIGHEST PRIORITY)

### 1.1 Critical README Elements 
- [x] Instructions for running application (locally)
- [x] Instructions for running with Docker
- [x] Testing instructions
- [x] Technology description and choice justification
- [x] List of implemented features
- [x] List of skipped features
- [x] What could be improved with more time
- [x] Compromises and trade-offs in decisions made
- [x] (Optional) High-level architectural diagram

## 2. Basic Swagger Documentation (MEDIUM PRIORITY)

### 2.1 Improving auto-generated API documentation
- [x] Configure detailed descriptions for all endpoints
- [x] Add request and response examples
- [x] Document authentication
- [x] Describe all data models with examples
- [x] Add tags and endpoint grouping
- [x] Document error responses

## 3. Adding Code Comments (LOW PRIORITY)

### 3.1 Code documentation
- [ ] Add docstrings to all functions and classes
- [ ] Document complex algorithms
- [ ] Add type hints where missing
- [ ] Document business rules in comments
- [ ] Add usage examples in docstrings

## 4. Performance Optimization (OPTIONAL - if time remains)

### 4.1 Database optimizations
- [ ] Add indexes for frequently used fields
- [ ] Optimize N+1 queries
- [ ] Add database connection pooling
- [ ] Implement eager/lazy loading where needed

### 4.2 API optimizations
- [ ] Add response caching where applicable
- [ ] Optimize response payload size
- [ ] Add compression middleware
- [ ] Implement pagination for large lists

## 5. Final Security Check (HIGH PRIORITY)

### 5.1 Pre-production Security audit
- [x] Check all endpoints for authorization
- [x] Validate all user inputs
- [x] Check password policies
- [x] Audit secret keys and tokens
- [ ] Check HTTPS settings (for production)
- [x] Rate limiting for API endpoints

### 5.2 Data protection
- [x] Ensure passwords are not logged
- [x] Check that sensitive data is not returned in API
- [x] Validate data access permissions
- [x] SQL injection protection through ORM

## Stage 7 Completion Criteria (prioritized)

### Must have for submission:
- [x] README.md contains all necessary information from requirements
- [x] Basic Swagger documentation works
- [x] Security checked and configured

### Nice to have (if time allows):
- [ ] API detailed documentation in Swagger
- [ ] Code well documented
- [ ] Performance optimized

### Time allocation recommendations:
- **60% of time**: README.md (this is key to good evaluation!)
- **30% of time**: Security audit
- **10% of time**: Documentation improvements

---

# TODO: Stage 8 - Adding CI/CD (GitHub Actions)

## 1. Continuous Integration (CI)
- [x] Create `.github/workflows/ci.yml` file
- [x] Configure triggers: `on: [push, pull_request]`
- [x] Step: `actions/checkout@v4`
- [x] Step: `actions/setup-python@v5` with `python-version: '3.11'` and pip cache
- [x] Install dev dependencies: `pip install -r requirements.dev.txt`
- [x] Run linters and static analysis:
  - [x] `flake8 .`
  - [x] `mypy app/`
- [x] Run tests with coverage:
  - [x] `pytest --cov=app --cov-report=xml`
- [x] Publish coverage report (e.g., via `codecov/codecov-action`)
- [x] (Optional) Build Docker image and push to GHCR

## 2. Continuous Deployment (CD)
- [x] Create `.github/workflows/cd.yml` file
- [x] Configure trigger: `on.push.tags: ['v*']`
- [x] Job: **deploy-staging**
  - [x] Configure environment: `staging`
  - [x] SSH access to server (via `appleboy/ssh-action`)
  - [x] Pull required Docker image from GHCR
  - [x] Run `docker-compose up -d --force-recreate`
- [x] Job: **deploy-production**
  - [x] Requires `approve` in environment: `production`
  - [x] Similar deployment script for prod
- [x] Add and save in GitHub Secrets:
  - `GHCR_TOKEN`, `STAGE_HOST`, `STAGE_USER`, `STAGE_KEY`
  - `PROD_HOST`, `PROD_USER`, `PROD_KEY`

## 3. Additional
- [x] Configure Dependabot (`.github/dependabot.yml`) for dependency updates
- [ ] Add CodeQL analysis (`.github/workflows/codeql.yml`)
- [ ] Docker layer caching (`actions/cache` + `docker/setup-buildx-action`)

---