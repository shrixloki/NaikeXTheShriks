.PHONY: dev test migrate lint db-up db-down

# Start the full local environment in Docker Compose
dev:
	docker compose up --build

# Run the pytest test suite
test:
	pytest

# Run database migrations
migrate:
	alembic upgrade head

# Run code style checking and linting using Ruff
lint:
	ruff check .
	ruff format --check .

# Spin up database and cache services in the background
db-up:
	docker compose up -d postgres redis

# Spin down all Docker Compose services
db-down:
	docker compose down
