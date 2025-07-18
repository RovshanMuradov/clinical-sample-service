# Clinical Sample Service

> A secure, production-ready REST API for managing clinical samples (blood, saliva, tissue) in medical research environments with enterprise-grade authentication and comprehensive Swagger documentation.

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd clinical-sample-service
docker-compose up --build

# 2. Access the API
open http://localhost:8000/docs  # Interactive Swagger UI
open http://localhost:8000/redoc # Alternative documentation
```

**System ready! 🎉**

---

## 📋 Table of Contents

1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Getting Started](#getting-started)
4. [API Documentation](#api-documentation)
5. [Testing](#testing)
6. [Project Documentation](#project-documentation)
7. [Security](#security)
8. [Implemented Features](#implemented-features)
9. [Known Limitations](#known-limitations)
10. [Trade-offs & Decisions](#trade-offs--decisions)

---

## ✨ Features

**Core Functionality:**
- ✅ **Complete CRUD Operations** - Create, read, update, delete clinical samples
- ✅ **JWT Authentication** - Secure user registration and login
- ✅ **Advanced Filtering** - Filter by type, status, subject ID, collection date
- ✅ **Data Isolation** - Users see only their own samples
- ✅ **Business Rule Validation** - Medical industry compliance rules
- ✅ **Statistics & Analytics** - Sample overview and reporting

**Documentation & API:**
- ✅ **Interactive Swagger UI** - Test APIs directly from browser
- ✅ **Comprehensive Documentation** - Detailed endpoint descriptions
- ✅ **Request/Response Examples** - Ready-to-use JSON examples
- ✅ **Authentication Testing** - Built-in JWT testing in Swagger
- ✅ **Error Documentation** - Standardized error responses

**Security & Production:**
- ✅ **Enterprise Security** - Rate limiting, request timeouts, security headers
- ✅ **Input Validation** - Comprehensive validation with business rules
- ✅ **SQL Injection Protection** - SQLAlchemy ORM protection
- ✅ **CI/CD Pipeline** - GitHub Actions with automated testing

---

## 🛠 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API** | FastAPI 0.116.1 | High performance, automatic OpenAPI generation |
| **Database** | PostgreSQL 15 + asyncpg | ACID transactions, async performance |
| **ORM** | SQLAlchemy 2.0.41 | Type-safe database operations |
| **Authentication** | JWT + bcrypt | Stateless, secure authentication |
| **Validation** | Pydantic 2.11.7 | Automatic data validation |
| **Testing** | pytest 8.4.1 | Comprehensive test coverage |
| **Deployment** | Docker + GitHub Actions | CI/CD automation |

**Architecture: Clean layered design**
```
FastAPI Endpoints → Service Layer → Repository Layer → PostgreSQL
       ↓              ↓              ↓
   Swagger UI    Business Logic   Data Access
```

---

## 🚀 Getting Started

**Option 1: Docker (Recommended)**
```bash
# Clone and run
git clone <repository-url>
cd clinical-sample-service
docker-compose up --build

# Access API
open http://localhost:8000/docs
```

**Option 2: Local Development**
```bash
# Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure and run
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

**🎯 Available Services:**
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 API Documentation

**🎯 Interactive Documentation:**
- **Swagger UI**: http://localhost:8000/docs - Test APIs directly
- **ReDoc**: http://localhost:8000/redoc - Alternative documentation
- **OpenAPI JSON**: http://localhost:8000/openapi.json - API specification

**✨ Documentation Features:**
- ✅ **Interactive Testing** - Test all endpoints directly in browser
- ✅ **Authentication Testing** - Built-in JWT token testing
- ✅ **Request/Response Examples** - Real JSON examples for all endpoints
- ✅ **Error Documentation** - Complete error response documentation
- ✅ **Business Rules** - Medical industry validation rules documented

**🔧 Quick API Test:**
```bash
# 1. Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "researcher", "email": "researcher@test.com", "password": "SecurePass!123"}'

# 2. Login and get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "researcher@test.com", "password": "SecurePass!123"}'

# 3. Create sample (use token from step 2)
curl -X POST "http://localhost:8000/api/v1/samples/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sample_type": "blood", "subject_id": "P001", "collection_date": "2025-01-15", "storage_location": "freezer-1-rowA"}'
```

---

## 🔒 Testing

**📊 Test Coverage:**
- **Total Tests**: 41 ✅
- **Success Rate**: 100% (41/41) ✅
- **Code Coverage**: 46.17%
- **Critical Security**: 95% covered ✅

**🧪 Run Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test category
pytest tests/test_auth.py -v
```

**Test Categories:**
- **Unit Tests**: Authentication, business logic, data validation
- **Integration Tests**: API endpoints, database operations
- **Security Tests**: Data isolation, input validation, JWT security
- **Edge Cases**: Error handling, invalid inputs, boundary conditions

---

## 📖 Project Documentation

**Comprehensive project documentation and testing results:**

- **[TODO.md](docs/TODO.md)** - Complete project implementation plan and progress tracking
- **[TESTING_API.md](docs/TESTING_API.md)** - Live API testing results (9/10 tests passed, data isolation verified)
- **[TESTING_REPORT.md](docs/TESTING_REPORT.md)** - Unit testing report (41/41 tests passed, 46.17% coverage)

**Key Testing Highlights:**
- ✅ **Security**: Data isolation, JWT authentication, password validation
- ✅ **Business Logic**: Medical compliance rules, input validation
- ✅ **API Coverage**: All CRUD operations, filtering, statistics
- ✅ **Database**: PostgreSQL integration, migrations, persistence

---

## 🔐 Security

**Enterprise-Grade Security Features:**
- ✅ **JWT Authentication** - Stateless tokens with configurable lifetime
- ✅ **Password Security** - bcrypt hashing, complexity requirements
- ✅ **Rate Limiting** - 60 requests/minute per IP
- ✅ **Data Isolation** - Strict user data separation
- ✅ **Input Validation** - Comprehensive validation with business rules
- ✅ **SQL Injection Protection** - SQLAlchemy ORM protection
- ✅ **Security Headers** - X-Content-Type-Options, X-Frame-Options, CSP
- ✅ **Medical Compliance** - Email domain validation, tissue storage rules

**Production Security:**
- Use HTTPS (enable ENABLE_HSTS=True)
- Configure strong PostgreSQL passwords
- Use external secret management
- Regular dependency updates

---

## ✅ Implemented Features

**🔐 Authentication & Authorization:**
- JWT tokens with configurable lifetime
- Secure password hashing (bcrypt)
- Email domain validation for medical data
- Password complexity checking

**📊 Sample Management:**
- Complete CRUD operations (create, read, update, delete)
- Support for 3 sample types: blood, saliva, tissue
- Status tracking: collected, processing, archived
- Storage location validation (freezer-X-rowY format)

**🔍 Advanced Filtering:**
- Filter by sample type, status, subject ID
- Filter by collection date (range)
- Combined filters with pagination
- Subject-specific sample queries

**🛡️ Security & Compliance:**
- Strict data isolation between users
- Medical industry business rule validation
- SQL injection protection
- Rate limiting and request timeout

**📚 Documentation:**
- Interactive Swagger UI with authentication testing
- Comprehensive endpoint documentation
- Request/response examples
- Error response documentation

---

## ⚠️ Known Limitations

**Not Implemented:**
- Sample file upload and storage
- Integration with external LIMS systems
- Advanced monitoring (Prometheus/Grafana)
- Caching for high-performance scenarios
- Audit trail for regulatory compliance

**Future Improvements:**
- [ ] Increase test coverage to 70%+
- [ ] Add file upload support
- [ ] Implement advanced search capabilities
- [ ] Add data export functionality
- [ ] Performance optimization with caching

---

## 🤔 Trade-offs & Decisions

**FastAPI vs Django REST Framework:**
- ✅ **Chose FastAPI** - Better performance, automatic OpenAPI generation
- ❌ **Trade-off** - Fewer ready-made solutions, more custom configuration

**JWT vs Session-based Auth:**
- ✅ **Chose JWT** - Stateless, scalability
- ❌ **Trade-off** - Harder token revocation, larger payload

**SQLAlchemy vs Raw SQL:**
- ✅ **Chose SQLAlchemy** - Security, migrations, type hints
- ❌ **Trade-off** - Small overhead, complexity for complex queries

---

## 🚀 Ready to Use!

**1. Start the system:**
```bash
docker-compose up --build
```

**2. Open documentation:**
```bash
open http://localhost:8000/docs
```

**3. Create your first user and start testing!**

> **Note:** This project prioritizes medical data security and production readiness. The comprehensive Swagger documentation allows for immediate API testing and integration.

---