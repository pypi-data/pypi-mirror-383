.PHONY: help install test lint format check migrate makemigrations shell clean

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package and dependencies
	uv sync --extra dev

test:  ## Run test suite
	PYTHONPATH=. uv run python tests/manage.py test

test-verbose:  ## Run tests with verbose output
	PYTHONPATH=. uv run python tests/manage.py test --verbosity=2

lint:  ## Run ruff linting
	uv run ruff check src/ tests/

format:  ## Auto-format code with ruff
	uv run ruff format src/ tests/

check:  ## Run all quality checks
	@echo "Running lint..."
	@make lint
	@echo "Running Django system check..."
	@PYTHONPATH=. uv run python tests/manage.py check
	@echo "All checks passed!"

migrate:  ## Run database migrations
	PYTHONPATH=. uv run python tests/manage.py migrate

makemigrations:  ## Create new migrations
	PYTHONPATH=. uv run python tests/manage.py makemigrations

shell:  ## Open Django shell
	PYTHONPATH=. uv run python tests/manage.py shell

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -f test_db.sqlite3
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .ruff_cache

build:  ## Build package
	uv build

publish-test:  ## Publish to TestPyPI
	uv publish --repository testpypi

publish:  ## Publish to PyPI
	uv publish
