# Makefile for hatch-simple-cython project

.PHONY: help install test test-unit test-integration test-examples test-structure test-cov lint format build build-examples clean

# Default target: show help information
help:
	@echo "hatch-simple-cython Makefile"
	@echo "============================"
	@echo ""
	@echo "Available commands:"
	@echo "  make install         - Install project dependencies"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-examples   - Run example tests"
	@echo "  make test-structure  - Check project structure"
	@echo "  make test-cov        - Run tests with coverage report"
	@echo "  make lint            - Run code linting"
	@echo "  make format          - Format code"
	@echo "  make build           - Build the project"
	@echo "  make build-examples  - Build example projects"
	@echo "  make clean           - Clean build artifacts"
	@echo ""

# Install project dependencies
install:
	@echo "Installing project dependencies..."
	uv sync

# Run all tests
test:
	@echo "Running tests..."
	uv run pytest tests/ -v

# Run unit tests
test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/test_plugin.py -v

# Run integration tests
test-integration:
	@echo "Running integration tests..."
	uv run pytest tests/test_integration.py -v

# Run example tests
test-examples:
	@echo "Running example tests..."
	uv run pytest tests/test_examples.py -v

# Check project structure
test-structure:
	@echo "Checking project structure..."
	uv run pytest tests/test_project_structure.py -v

# Run all tests with coverage report
test-cov:
	@echo "Running tests with coverage..."
	uv run pytest tests/ -v --cov=src/hatch_simple_cython --cov-report=term --cov-report=html

# Run code linting
lint:
	@echo "Running code linting..."
	@echo "Note: Install ruff with 'uv pip install ruff'"
	uv run ruff check src/ tests/

# Format code
format:
	@echo "Formatting code..."
	@echo "Note: Install ruff with 'uv pip install ruff'"
	uv run ruff format src/ tests/

# Build the project
build:
	@echo "Building project..."
	uv build

# Build example projects
build-examples:
	@echo "Building simple_example..."
	cd examples/simple_example && uv build
	@echo ""
	@echo "Building numpy_example..."
	cd examples/numpy_example && uv build


# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	-rm -rf dist/ build/ *.egg-info
	-rm -rf src/hatch_simple_cython/__pycache__
	-rm -rf tests/__pycache__
	-rm -rf .pytest_cache
	-rm -rf htmlcov
	-rm -rf .coverage
	-find . -type d -name "__pycache__" -exec rm -rf {} +
	-find . -type f -name "*.pyc" -delete
	-find . -type f -name "*.pyo" -delete
	-find . -type f -name "*.so" -delete
	-find . -type f -name "*.c" -delete
	-cd examples/simple_example && rm -rf dist/ build/ *.egg-info
	-cd examples/numpy_example && rm -rf dist/ build/ *.egg-info
	@echo "✓ Cleanup complete"
