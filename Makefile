# MFinance - Makefile for Docker Management
.PHONY: help build up down restart logs clean test lint format

# Default target
help:
	@echo "MFinance - Financial Management System"
	@echo "Available commands:"
	@echo "  build          - Build all Docker images"
	@echo "  up             - Start all services in development mode"
	@echo "  up-prod        - Start all services in production mode"
	@echo "  down           - Stop all services"
	@echo "  restart        - Restart all services"
	@echo "  logs           - Show logs for all services"
	@echo "  logs-backend   - Show backend logs"
	@echo "  logs-frontend  - Show frontend logs"
	@echo "  clean          - Clean up containers and volumes"
	@echo "  test           - Run tests"
	@echo "  test-backend   - Run backend tests"
	@echo "  test-frontend  - Run frontend tests"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  migrate        - Run database migrations"
	@echo "  shell-backend  - Open backend shell"
	@echo "  shell-frontend - Open frontend shell"
	@echo "  status         - Show service status"

# Build all images
build:
	docker-compose build

# Start development environment
up:
	docker-compose up -d
	@echo "Services started:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Admin:    http://localhost:8000/admin"
	@echo "  Grafana:  http://localhost:3001 (admin/admin)"
	@echo "  MinIO:    http://localhost:9000 (minioadmin/minioadmin)"

# Start production environment
up-prod:
	docker-compose -f docker-compose.prod.yml up -d

# Stop all services
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# Show logs
logs:
	docker-compose logs -f

# Show backend logs
logs-backend:
	docker-compose logs -f backend worker beat

# Show frontend logs
logs-frontend:
	docker-compose logs -f frontend

# Clean up
clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Run all tests
test:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Run backend tests
test-backend:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit backend-test

# Run frontend tests
test-frontend:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit frontend-test

# Run linting
lint:
	docker-compose exec backend flake8 .
	docker-compose exec frontend npm run lint

# Format code
format:
	docker-compose exec backend black .
	docker-compose exec backend isort .
	docker-compose exec frontend npm run format

# Run migrations
migrate:
	docker-compose exec backend python manage.py migrate

# Open backend shell
shell-backend:
	docker-compose exec backend python manage.py shell

# Open frontend shell
shell-frontend:
	docker-compose exec frontend sh

# Show service status
status:
	docker-compose ps

# Create superuser
createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

# Load test data
loaddata:
	docker-compose exec backend python manage.py loaddata fixtures/test_data.json

# Collect static files
collectstatic:
	docker-compose exec backend python manage.py collectstatic --noinput

# Backup database
backup:
	docker-compose exec postgres pg_dump -U postgres mfinance > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Restore database
restore:
	docker-compose exec -T postgres psql -U postgres mfinance < $(FILE)

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "✅ Frontend: OK" || echo "❌ Frontend: DOWN"
	@curl -f http://localhost:8000/health/ > /dev/null 2>&1 && echo "✅ Backend: OK" || echo "❌ Backend: DOWN"
	@curl -f http://localhost:3001 > /dev/null 2>&1 && echo "✅ Grafana: OK" || echo "❌ Grafana: DOWN"
	@curl -f http://localhost:9000 > /dev/null 2>&1 && echo "✅ MinIO: OK" || echo "❌ MinIO: DOWN"
