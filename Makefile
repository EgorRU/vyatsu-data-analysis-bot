.PHONY: help install install-dev test lint format clean run

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

run: ## Run the bot
	python main.py

setup: ## Initial setup of the project
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  # Linux/macOS"
	@echo "  venv\\Scripts\\activate     # Windows"

check: ## Run all checks (lint + test)
	$(MAKE) lint
	$(MAKE) test

dev-setup: setup install-dev ## Complete development setup
	@echo "Development environment ready!"

# Docker commands (if needed later)
docker-build: ## Build Docker image
	docker build -t vyatsu-data-analysis-bot .

docker-run: ## Run Docker container
	docker run -it --env-file .env vyatsu-data-analysis-bot

# Database commands
db-init: ## Initialize database
	python -c "from models import init_db; import asyncio; asyncio.run(init_db())"

# Utility commands
env-check: ## Check environment variables
	@echo "Checking environment variables..."
	@python -c "from settings import settings; print('✅ Environment loaded successfully')"
