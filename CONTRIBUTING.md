# Contributing to Clinical Sample Service

Thank you for considering contributing to the Clinical Sample Service! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/clinical-sample-service.git
   cd clinical-sample-service
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/original-owner/clinical-sample-service.git
   ```
4. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- A clear and descriptive title
- Detailed description of the proposed enhancement
- Use cases and benefits
- Possible implementation approach (if applicable)

### Pull Requests

1. Ensure your code follows the project's style guidelines
2. Include appropriate tests for your changes
3. Update documentation as needed
4. Ensure all tests pass locally
5. Write a clear commit message following conventional commits format

## Development Process

### Setting Up Development Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements/dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_samples.py -v

# Run linting
flake8 app/ tests/
mypy app/
black app/ tests/ --check
isort app/ tests/ --check
```

## Style Guidelines

### Python Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting (line length: 100)
- Use isort for import sorting
- Type hints are required for all functions
- Maximum function length: 50 lines
- Maximum file length: 500 lines

### Commit Messages

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(auth): add refresh token endpoint

Implement JWT refresh token functionality to allow users
to obtain new access tokens without re-authentication.

Closes #123
```

### Documentation

- Update README.md if adding new features
- Add docstrings to all public functions and classes
- Include type hints in function signatures
- Update API documentation for endpoint changes

## Testing

### Test Requirements

- All new features must include tests
- Maintain or improve code coverage (minimum 70%)
- Include both unit and integration tests where applicable
- Test edge cases and error conditions

### Writing Tests

```python
def test_sample_creation_with_valid_data(
    client: TestClient,
    db_session: Session,
    auth_headers: dict
):
    """Test creating a sample with valid data."""
    sample_data = {
        "sample_type": "blood",
        "subject_id": "P001",
        "collection_date": "2025-01-20",
        "storage_location": "freezer-1-rowA"
    }
    
    response = client.post(
        "/api/v1/samples/",
        json=sample_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["sample_type"] == "blood"
```

## Submitting Changes

### Pull Request Process

1. Update your branch with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request on GitHub with:
   - Clear title and description
   - Reference to any related issues
   - Screenshots (if UI changes)
   - Test results

4. Address review comments promptly

5. Once approved, your PR will be merged

### Review Criteria

Pull requests will be reviewed for:

- Code quality and style compliance
- Test coverage and quality
- Documentation updates
- Security implications
- Performance impact
- Alignment with project goals

## Questions?

If you have questions about contributing, please:

1. Check the [documentation](docs/)
2. Search existing issues
3. Create a new issue with the "question" label

Thank you for contributing to Clinical Sample Service!