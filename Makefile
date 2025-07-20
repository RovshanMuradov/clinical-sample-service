# Clinical Sample Service Makefile
# Usage: make <target>

.PHONY: help setup install dev docker-build docker-up docker-down docker-logs test lint format clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
YELLOW := \033[33m
GREEN := \033[32m
RED := \033[31m
RESET := \033[0m

## Help
help: ## Show this help message
	@echo "$(GREEN)Clinical Sample Service - Available Commands:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'

## Setup & Installation
setup: ## Setup virtual environment and install dependencies
	@echo "$(GREEN)Setting up virtual environment...$(RESET)"
	python3.11 -m venv venv
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements/dev.txt
	@echo "$(GREEN)Setup complete! Run 'source venv/bin/activate' to activate the environment$(RESET)"

install: ## Install/update dependencies
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	./venv/bin/pip install -r requirements/dev.txt

## Development
dev: ## Run development server locally
	@echo "$(GREEN)Starting development server...$(RESET)"
	./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-logs: ## Show development server logs
	@echo "$(GREEN)Checking logs...$(RESET)"
	tail -f logs/clinical_sample_service.log

## Docker Commands
docker-build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(RESET)"
	cd docker && docker-compose build

docker-up: ## Start all services with Docker
	@echo "$(GREEN)Starting Docker services...$(RESET)"
	cd docker && docker-compose up -d
	@echo "$(GREEN)Services started! Check status with 'make docker-status'$(RESET)"

docker-up-logs: ## Start all services with Docker and show logs
	@echo "$(GREEN)Starting Docker services with logs...$(RESET)"
	cd docker && docker-compose up

docker-down: ## Stop all Docker services
	@echo "$(GREEN)Stopping Docker services...$(RESET)"
	cd docker && docker-compose down

docker-restart: ## Restart Docker services
	@echo "$(GREEN)Restarting Docker services...$(RESET)"
	cd docker && docker-compose restart

docker-logs: ## Show Docker logs
	@echo "$(GREEN)Showing Docker logs...$(RESET)"
	cd docker && docker-compose logs -f

docker-status: ## Show Docker services status
	@echo "$(GREEN)Docker services status:$(RESET)"
	cd docker && docker-compose ps

docker-shell: ## Access application container shell
	@echo "$(GREEN)Accessing application container...$(RESET)"
	cd docker && docker-compose exec app bash

docker-db-shell: ## Access database container shell
	@echo "$(GREEN)Accessing database container...$(RESET)"
	cd docker && docker-compose exec db psql -U clinical_user -d clinical_samples_db

## Database Commands
migrate-create: ## Create new migration (Usage: make migrate-create MESSAGE="description")
	@echo "$(GREEN)Creating new migration...$(RESET)"
	./venv/bin/alembic revision --autogenerate -m "$(MESSAGE)"

migrate-up: ## Apply migrations
	@echo "$(GREEN)Applying migrations...$(RESET)"
	./venv/bin/alembic upgrade head

migrate-down: ## Downgrade last migration
	@echo "$(YELLOW)Downgrading last migration...$(RESET)"
	./venv/bin/alembic downgrade -1

migrate-history: ## Show migration history
	@echo "$(GREEN)Migration history:$(RESET)"
	./venv/bin/alembic history

migrate-current: ## Show current migration
	@echo "$(GREEN)Current migration:$(RESET)"
	./venv/bin/alembic current

## Testing
test: ## Run all tests
	@echo "$(GREEN)Running tests...$(RESET)"
	./venv/bin/pytest

test-cov: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(RESET)"
	./venv/bin/pytest --cov=app --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(RESET)"
	./venv/bin/pytest-watch

## Code Quality
lint: ## Run linting
	@echo "$(GREEN)Running linting...$(RESET)"
	./venv/bin/flake8 app/ tests/

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(RESET)"
	./venv/bin/black app/ tests/
	./venv/bin/isort app/ tests/

typecheck: ## Run type checking
	@echo "$(GREEN)Running type checking...$(RESET)"
	./venv/bin/mypy app/

quality: lint typecheck ## Run all code quality checks

## Health Checks
health: ## Check API health
	@echo "$(GREEN)Checking API health...$(RESET)"
	curl -f http://localhost:8000/health || echo "$(RED)API is not running$(RESET)"

api-docs: ## Open API documentation
	@echo "$(GREEN)Opening API docs...$(RESET)"
	open http://localhost:8000/docs || echo "Visit: http://localhost:8000/docs"

## Cleanup
clean: ## Clean up temporary files and caches
	@echo "$(GREEN)Cleaning up...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-docker: ## Clean up Docker resources
	@echo "$(GREEN)Cleaning Docker resources...$(RESET)"
	cd docker && docker-compose down -v
	docker system prune -f

## Quick Start Commands
start: docker-up ## Quick start with Docker (alias for docker-up)

stop: docker-down ## Quick stop (alias for docker-down)

restart: docker-restart ## Quick restart (alias for docker-restart)

logs: docker-logs ## Quick logs (alias for docker-logs)

shell: docker-shell ## Quick shell access (alias for docker-shell)

## Full Workflow Commands
first-run: setup docker-build docker-up ## Complete first-time setup and start
	@echo "$(GREEN)First run complete! API should be available at http://localhost:8000$(RESET)"
	@echo "$(GREEN)API docs: http://localhost:8000/docs$(RESET)"
	@echo "$(GREEN)Health check: make health$(RESET)"

full-test: format lint typecheck test ## Run complete test suite

rebuild: docker-down docker-build docker-up ## Full rebuild and restart