.PHONY: help build up down restart logs clean seed prepare-kb test

# Default target
help:
	@echo "BookLeaf AI Assistant - Docker Commands"
	@echo "=========================================="
	@echo ""
	@echo "Production Mode:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo ""
	@echo "Development Mode:"
	@echo "  make dev-up         - Start services in dev mode (hot reload)"
	@echo "  make dev-down       - Stop dev services"
	@echo "  make dev-logs       - View dev logs"
	@echo ""
	@echo "Database:"
	@echo "  make seed           - Seed database with mock authors"
	@echo "  make prepare-kb     - Generate knowledge base embeddings"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Remove containers, volumes, and images"
	@echo "  make test           - Run backend tests"
	@echo "  make shell-backend  - Access backend container shell"
	@echo "  make shell-frontend - Access frontend container shell"
	@echo ""

# Production commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

# Development commands
dev-up:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development services started!"
	@echo "Frontend: http://localhost:3000 (with hot reload)"
	@echo "Backend: http://localhost:8000 (with hot reload)"

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Database commands
seed:
	@echo "Seeding database..."
	docker-compose exec backend bash -c "echo 'n' | python scripts/seed_data.py"

prepare-kb:
	@echo "Generating knowledge base embeddings..."
	docker-compose exec backend python scripts/prepare_knowledge_base.py

# Maintenance commands
clean:
	docker-compose down -v --rmi all
	@echo "All containers, volumes, and images removed"

test:
	docker-compose exec backend pytest

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

# Status check
status:
	docker-compose ps

# View specific service logs
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Quick start (build + up + seed)
quickstart: build up
	@echo "Waiting for services to be healthy..."
	@sleep 30
	@make seed
	@make prepare-kb
	@echo ""
	@echo "✅ Application is ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
