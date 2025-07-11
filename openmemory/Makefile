.PHONY: help up down logs shell migrate test test-clean env ui-install ui-start ui-dev ui-build ui-dev-start build clean upgrade downgrade backup backup-sql backup-qdrant

# Default target
help:
	@echo "Available commands:"
	@echo "  make env       - Copy env.example to .env"
	@echo "  make build     - Build the containers"
	@echo "  make up        - Start the containers"
	@echo "  make down      - Stop the containers"
	@echo "  make clean     - Stop containers and clean up volumes"
	@echo "  make logs      - Show container logs"
	@echo "  make shell     - Open a shell in the api container"
	@echo "  make migrate   - Run database migrations"
	@echo "  make upgrade   - Run database migrations (alias for migrate)"
	@echo "  make downgrade - Rollback database migrations"
	@echo "  make test      - Run tests in a new container"
	@echo "  make test-clean - Run tests and clean up volumes"
	@echo "  make ui-install - Install frontend dependencies"
	@echo "  make ui-start  - Start the frontend development server"
	@echo "  make ui-dev    - Install dependencies and start the frontend in dev mode"
	@echo "  make ui        - Install dependencies and start the frontend in production mode"
	@echo "  make backup    - Run full backup (SQL + Qdrant)"
	@echo "  make backup-sql - Backup SQL database only"
	@echo "  make backup-qdrant - Backup Qdrant vector database only"

env:
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template. Please edit it with your settings."; \
	else \
		echo ".env file already exists. Skipping creation."; \
	fi

build:
	docker compose build --no-cache

up:
	@echo "Starting OpenMemory..."
	@if [ ! -f .env ]; then \
		echo "No .env file found. Run 'make env' to create one."; \
		exit 1; \
	fi
	@export $(shell grep -v '^#' .env | xargs) && \
	if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "OPENAI_API_KEY not set. Please set it in your .env file."; \
		echo "Example: OPENAI_API_KEY=sk-your-openai-api-key-here"; \
		exit 1; \
	fi
	docker compose up -d
	@echo "OpenMemory is starting up!"
	@echo "  API: http://localhost:8765"
	@echo "  UI: http://localhost:3000"
	@echo "  API Docs: http://localhost:8765/docs"

down:
	docker compose down -v

clean:
	docker compose down -v
	rm -f api/openmemory.db

logs:
	docker compose logs -f

shell:
	docker compose exec api bash

upgrade:
	docker compose exec api alembic upgrade head

migrate:
	docker compose exec api alembic upgrade head

downgrade:
	docker compose exec api alembic downgrade -1

ui-dev:
	cd ui && NEXT_PUBLIC_USER_ID=$(USER) NEXT_PUBLIC_API_URL=$(NEXT_PUBLIC_API_URL) pnpm install && pnpm dev

# Backup commands
backup:
	@echo "Running full backup..."
	@if [ ! -f .env ]; then \
		echo "No .env file found. Run 'make env' to create one."; \
		exit 1; \
	fi
	@source .env && ./scripts/backup_all.sh

backup-sql:
	@echo "Running SQL database backup..."
	@if [ ! -f .env ]; then \
		echo "No .env file found. Run 'make env' to create one."; \
		exit 1; \
	fi
	@source .env && ./scripts/backup_postgresql.sh || ./scripts/backup_mysql.sh || ./scripts/backup_sqlite.sh

backup-qdrant:
	@echo "Running Qdrant vector database backup..."
	@if [ ! -f .env ]; then \
		echo "No .env file found. Run 'make env' to create one."; \
		exit 1; \
	fi
	@source .env && ./scripts/backup_qdrant.sh
