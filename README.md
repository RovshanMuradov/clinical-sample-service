# Clinical Sample Service

[![CI Status](https://github.com/RovshanMuradov/clinical-sample-service/workflows/CI/badge.svg)](https://github.com/RovshanMuradov/clinical-sample-service/actions)
[![Coverage](https://codecov.io/gh/RovshanMuradov/clinical-sample-service/branch/main/graph/badge.svg)](https://codecov.io/gh/RovshanMuradov/clinical-sample-service)
[![Latest Release](https://img.shields.io/github/v/release/RovshanMuradov/clinical-sample-service)](https://github.com/RovshanMuradov/clinical-sample-service/releases)
[![Code of Conduct](https://img.shields.io/badge/CoC-Contributor%20Covenant-brightgreen)](CODE_OF_CONDUCT.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A secure, production-ready REST API for managing clinical samples (blood, saliva, tissue) in medical research environments with enterprise-grade authentication and comprehensive API documentation.

## Live Demo

**🚀 [clinical-api-demo](https://rovshanmuradov.github.io/clinical-api-demo/)** - Interactive demonstration with auto-redirect to live API documentation

## Table of Contents

- [Live Demo](#live-demo)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Security](#security)
- [Testing](#testing)
- [Design Decisions & Limitations](#design-decisions--limitations)
- [Additional Docs](#additional-docs)
- [Contributing](#contributing)
- [License](#license)

## Features

**Core Functionality:**
- Complete CRUD operations for clinical sample management
- JWT-based authentication with secure user registration and login
- Advanced filtering by sample type, status, subject ID, and collection date
- Strict data isolation - users access only their own samples
- Medical industry compliance with business rule validation
- Sample statistics and analytics dashboard

<details>
  <summary><strong>Technical Features</strong></summary>

- Comprehensive API documentation with interactive testing
- Request/response validation using Pydantic schemas
- Async database operations with PostgreSQL and asyncpg
- Automated database migrations with Alembic
- Enterprise security features (rate limiting, security headers)
- CI/CD pipeline with GitHub Actions
</details>

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API** | FastAPI 0.116.1 | High performance async framework with automatic OpenAPI |
| **Database** | PostgreSQL 15 + asyncpg | ACID compliance with async performance |
| **ORM** | SQLAlchemy 2.0.41 | Type-safe database operations |
| **Authentication** | JWT + bcrypt | Stateless secure authentication |
| **Validation** | Pydantic 2.9.2 | Automatic request/response validation |
| **Testing** | pytest 8.4.1 | Comprehensive test coverage |
| **Deployment** | AWS SAM + GitHub Actions | Serverless deployment with CI/CD |
| **Infrastructure** | AWS Lambda + API Gateway | Production serverless architecture |

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- Python 3.11 (for local development)
- PostgreSQL 15 (for local development without Docker)

### Quick Start with Docker

```bash
# Option 1: Pull from Docker Hub (if available)
docker pull rovshanmuradov/clinical-sample-service:latest

# Option 2: Build from source
git clone https://github.com/RovshanMuradov/clinical-sample-service.git
cd clinical-sample-service
docker compose up --build

# API is now available at http://localhost:8000
# Interactive documentation at http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Configure environment
cp .env.example .env
# Edit .env file with your credentials

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Environment Variables

| Variable | Description | Example |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/db` |
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) | `abc123...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token lifetime | `30` |
| `DEBUG` | Enable debug mode | `True` / `False` |
| `LOG_LEVEL` | Logging level | `INFO` / `DEBUG` / `ERROR` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` |
| `REQUEST_TIMEOUT_SECONDS` | Request timeout | `30` |

## API Documentation

### Live Production API
- **Interactive API Explorer**: [clinical-api-demo](https://rovshanmuradov.github.io/clinical-api-demo/) (auto-redirects to live docs)
- **Swagger UI Documentation**: https://7wi1s6opc8.execute-api.eu-north-1.amazonaws.com/Prod/docs
- **ReDoc Documentation**: https://7wi1s6opc8.execute-api.eu-north-1.amazonaws.com/Prod/redoc
- **OpenAPI Schema**: https://7wi1s6opc8.execute-api.eu-north-1.amazonaws.com/Prod/openapi.json

### Local Development
- **Interactive API Explorer**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

<details>
  <summary>Endpoints Overview</summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | User registration |
| `POST` | `/api/v1/auth/login` | User authentication |
| `GET`  | `/api/v1/samples` | List samples with filtering |
| `POST` | `/api/v1/samples` | Create new sample |
| `GET`  | `/api/v1/samples/{id}` | Get sample by ID |
| `PUT`  | `/api/v1/samples/{id}` | Update sample |
| `DELETE` | `/api/v1/samples/{id}` | Delete sample |
| `GET` | `/api/v1/samples/stats/overview` | Sample statistics |
</details>

### Quick API Test

#### Production API (Live Demo)
```bash
API_BASE="https://7wi1s6opc8.execute-api.eu-north-1.amazonaws.com/Prod"

# 1. Register a new user
curl -X POST "${API_BASE}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "researcher@test.com", "password": "SecurePass!123"}'

# 2. Login to get JWT token
curl -X POST "${API_BASE}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "researcher@test.com", "password": "SecurePass!123"}'

# 3. Create a sample (use token from step 2)
curl -X POST "${API_BASE}/api/v1/samples" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sample_type": "blood", "subject_id": "P001", "collection_date": "2025-01-20T10:00:00Z", "storage_location": "freezer-1-rowA"}'
```

#### Local Development
```bash
API_BASE="http://localhost:8000"

# 1. Register a new user
curl -X POST "${API_BASE}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "researcher", "email": "researcher@test.com", "password": "SecurePass!123"}'

# 2. Login to get JWT token
curl -X POST "${API_BASE}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "researcher@test.com", "password": "SecurePass!123"}'

# 3. Create a sample (use token from step 2)
curl -X POST "${API_BASE}/api/v1/samples/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sample_type": "blood", "subject_id": "P001", "collection_date": "2025-01-20", "storage_location": "freezer-1-rowA"}'
```

## Architecture

The application follows a clean layered architecture:

```mermaid
graph TD
    A[Client Request] --> B[FastAPI Router]
    B --> C[Authentication Middleware]
    C --> D[API Endpoints]
    D --> E[Service Layer]
    E --> F[Repository Layer]
    F --> G[SQLAlchemy ORM]
    G --> H[(PostgreSQL Database)]
    
    D --> I[Pydantic Schemas]
    E --> J[Business Rules]
    F --> K[Database Models]
    
    L[JWT Tokens] --> C
    M[Rate Limiting] --> C
    N[Security Headers] --> C
```

**Layer Responsibilities:**
- **API Layer**: FastAPI routes, request/response validation (Pydantic)
- **Service Layer**: Business logic, medical compliance rules, user authorization
- **Repository Layer**: Database operations abstraction, data access patterns
- **Models**: SQLAlchemy ORM models with relationships and constraints
- **Middleware**: Authentication, rate limiting, security headers, logging

## Security

**Authentication & Authorization:**
- JWT tokens with configurable expiration
- Bcrypt password hashing
- Strict data isolation between users
- Email domain validation for medical compliance

**API Protection:**
- Rate limiting (60 requests/minute per IP)
- Comprehensive input validation
- SQL injection protection via SQLAlchemy ORM
- Security headers (X-Content-Type-Options, X-Frame-Options, CSP)

**Performance & Hardening:**
- Request timeout (30 seconds)
- Payload size validation
- Connection pooling with async database operations

**Medical Data Compliance:**
- Business rule validation for sample storage
- Audit-ready data isolation
- Secure password requirements
- Authorized email domains only

## Testing

- **Unit Tests**: 41 tests with 100% pass rate
- **Code Coverage**: Target 50% (current ~46%)
- **Security Coverage**: 95% of critical risks covered
- **Integration Tests**: All API endpoints tested

Run tests:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_samples.py -v
```

## Design Decisions & Limitations

### Key Design Decisions

- **FastAPI over Django REST Framework**: Superior async performance and automatic OpenAPI generation, but requires more custom configuration
- **JWT over Session-based Auth**: Better scalability for microservices, but harder token revocation and larger payload overhead
- **SQLAlchemy over Raw SQL**: Type safety and SQL injection protection, but adds complexity for advanced queries
- **Alembic over Prisma**: Better Python ecosystem integration, but more manual migration management
- **PostgreSQL with asyncpg**: Enterprise reliability with async performance, but no built-in connection pooling

### Known Limitations

- File upload functionality not implemented
- No integration with external LIMS systems
- Test coverage below industry standard (70%)
- No built-in data export functionality
- Limited to 3 sample types (blood, saliva, tissue)

### Future Improvements

- Increase test coverage to 70%+
- Implement file upload for sample documentation
- Add data export functionality (CSV, Excel)
- Integrate with external laboratory systems
- Add real-time notifications for sample status changes

## Additional Docs

- **[clinical-api-demo](https://rovshanmuradov.github.io/clinical-api-demo/)** - Interactive live demonstration with professional presentation
- [Implementation Plan](docs/TODO.md) - Detailed project roadmap and progress tracking
- [API Testing Report](docs/TESTING_API.md) - Live API test results and verification
- [Unit Testing Report](docs/TESTING_REPORT.md) - Comprehensive test coverage analysis

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

