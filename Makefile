# MFinance Makefile

.PHONY: help install test test-backend test-frontend test-e2e test-coverage clean dev build

# Default target
help:
	@echo "MFinance - Available commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install          Install all dependencies"
	@echo "  install-backend  Install backend dependencies"
	@echo "  install-frontend Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev              Start development environment"
	@echo "  dev-backend      Start backend development server"
	@echo "  dev-frontend     Start frontend development server"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-backend     Run backend tests"
	@echo "  test-frontend    Run frontend tests"
	@echo "  test-e2e         Run E2E tests"
	@echo "  test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Database:"
	@echo "  migrate          Run database migrations"
	@echo "  migrate-backend  Run backend migrations"
	@echo "  superuser        Create Django superuser"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-up        Start Docker containers"
	@echo "  docker-down      Stop Docker containers"
	@echo "  docker-logs      View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean temporary files"
	@echo "  lint             Run linting"
	@echo "  format           Format code"

# Installation
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend/web-cabinet && npm install

# Development
dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "Development environment started. Access:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Keycloak: http://localhost:8080"

dev-backend:
	@echo "Starting backend development server..."
	cd backend && python manage.py runserver

dev-frontend:
	@echo "Starting frontend development server..."
	cd frontend/web-cabinet && npm run dev

# Testing
test: test-backend test-frontend test-e2e

test-backend:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

test-frontend:
	@echo "Running frontend tests..."
	cd frontend/web-cabinet && npm test

test-e2e:
	@echo "Running E2E tests..."
	cd frontend/web-cabinet && npx playwright test

test-coverage:
	@echo "Running tests with coverage..."
	cd backend && python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=80

# Database
migrate: migrate-backend

migrate-backend:
	@echo "Running backend migrations..."
	cd backend && python manage.py makemigrations
	cd backend && python manage.py migrate

superuser:
	@echo "Creating Django superuser..."
	cd backend && python manage.py createsuperuser

# Docker
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "Viewing Docker logs..."
	docker-compose logs -f

# Utilities
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov" -delete
	find . -type d -name "test-results" -delete
	find . -type d -name "node_modules" -delete
	find . -type f -name "package-lock.json" -delete

lint:
	@echo "Running linting..."
	cd backend && python -m flake8 .
	cd frontend/web-cabinet && npm run lint

format:
	@echo "Formatting code..."
	cd backend && python -m black .
	cd frontend/web-cabinet && npm run format

# Test specific modules
test-auth:
	@echo "Running auth system tests..."
	cd backend && python -m pytest tests/test_auth_system.py -v

test-finance:
	@echo "Running finance module tests..."
	cd backend && python -m pytest tests/test_finance.py -v

test-payments:
	@echo "Running payments module tests..."
	cd backend && python -m pytest tests/test_payments.py -v

test-fop:
	@echo "Running FOP module tests..."
	cd backend && python -m pytest tests/test_fop.py -v

test-reports:
	@echo "Running reports module tests..."
	cd backend && python -m pytest tests/test_reports.py -v

# Setup commands
setup-keycloak:
	@echo "Setting up Keycloak..."
	cd backend && python scripts/setup-keycloak.py

setup-payment-providers:
	@echo "Setting up payment providers..."
	cd backend && python manage.py setup_payment_providers

setup-report-templates:
	@echo "Setting up report templates..."
	cd backend && python manage.py setup_report_templates

# Full setup
setup: install migrate setup-keycloak setup-payment-providers setup-report-templates
	@echo "MFinance setup complete!"
	@echo "Run 'make dev' to start the development environment."