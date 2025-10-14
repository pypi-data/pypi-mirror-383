# Makefile for sdp-tools package

.PHONY: help install install-dev test test-fast test-slow test-coverage clean build lint format check docs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in production mode
	uv pip install .

install-dev:  ## Install package in development mode with all dependencies
	uv pip install -e ".[dev,test]"

test:  ## Run all tests
	pytest tests/ -v

test-fast:  ## Run fast tests only (skip slow tests)
	pytest tests/ -v -m "not slow"

test-slow:  ## Run slow tests only
	pytest tests/ -v -m "slow"

test-coverage:  ## Run tests with coverage report
	pytest tests/ --cov=sdp_tools --cov-report=html --cov-report=term-missing

test-imports:  ## Test package imports specifically
	pytest tests/test_imports.py -v

test-functionality:  ## Test core functionality
	pytest tests/test_functionality.py -v

test-build:  ## Test package building and distribution
	pytest tests/test_build_and_distribution.py -v

lint:  ## Run all linting tools
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	# mypy src/sdp_tools/ || echo "⚠️  mypy check completed with issues"

format:  ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

check:  ## Run all quality checks (lint + tests)
	@echo "Running linting..."
	$(MAKE) lint
	@echo "Running tests..."
	$(MAKE) test-fast

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package distributions
	$(MAKE) clean
	uv build

build-check:  ## Build and verify package
	$(MAKE) build
	twine check dist/*

docs:  ## Build documentation
	mkdocs build

docs-serve:  ## Serve documentation locally
	mkdocs serve

pre-commit:  ## Run pre-commit checks
	pre-commit run --all-files

install-pre-commit:  ## Install pre-commit hooks
	pre-commit install

# Development workflow commands
dev-setup:  ## Complete development setup
	$(MAKE) install-dev
	$(MAKE) install-pre-commit

quick-test:  ## Quick development test (imports + fast tests)
	@echo "Testing imports..."
	python -c "import sdp_tools; print('✓ Package imports successfully')"
	@echo "Running fast tests..."
	pytest tests/test_imports.py tests/test_functionality.py -v -x

# CI/CD simulation
ci:  ## Simulate CI pipeline
	@echo "=== CI Pipeline ==="
	@echo "1. Linting..."
	$(MAKE) lint
	@echo "2. Testing..."
	$(MAKE) test
	@echo "3. Building..."
	$(MAKE) build-check
	@echo "=== CI Complete ==="

# Release workflow
release-check:  ## Check if ready for release
	@echo "=== Release Readiness Check ==="
	@echo "1. Running full test suite..."
	$(MAKE) test
	@echo "2. Checking code quality..."
	$(MAKE) lint
	@echo "3. Building package..."
	$(MAKE) build-check
	@echo "4. Testing installation..."
	$(MAKE) test-build
	@echo "=== Release Ready ==="
