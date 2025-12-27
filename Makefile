.PHONY: help install sync test format lint check clean run-fava

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install uv package manager
	curl -LsSf https://astral.sh/uv/install.sh | sh

sync:  ## Sync dependencies from lockfile
	uv sync --extra dev

test:  ## Run test suite
	uv run pytest tests/ -v

test-cov:  ## Run tests with coverage report
	uv run pytest tests/ -v --cov --cov-report=html --cov-report=term

format:  ## Format code with ruff
	uv run ruff format .

lint:  ## Run linter with auto-fix
	uv run ruff check --fix .

check:  ## Check code quality (format + lint, no fixes)
	uv run ruff format --check .
	uv run ruff check .

typecheck:  ## Run mypy type checking
	uv run mypy ingestion plugins

pre-commit:  ## Run all pre-commit hooks
	uv run pre-commit run --all-files

pre-commit-install:  ## Install pre-commit hooks
	uv run pre-commit install

clean:  ## Clean up generated files
	rm -rf .venv/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-fava:  ## Start Fava web interface
	uv run fava ledger/main.bean

run-ingestion:  ## Run data ingestion
	uv run python ingestion/runner.py

bean-check:  ## Check Beancount ledger syntax
	uv run bean-check ledger/main.bean

add-dep:  ## Add a runtime dependency (usage: make add-dep PKG=package-name)
	uv add $(PKG)

add-dev-dep:  ## Add a dev dependency (usage: make add-dev-dep PKG=package-name)
	uv add --dev $(PKG)

update:  ## Update all dependencies
	uv lock --upgrade
	uv sync
