.PHONY: help install install-dev test test-unit test-integration coverage lint format typecheck docs clean build

help:
	@echo "Available commands:"
	@echo "  make install         Install package in production mode"
	@echo "  make install-dev     Install package with dev dependencies"
	@echo "  make test            Run all tests with coverage"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make coverage        Run tests and generate HTML coverage report"
	@echo "  make lint            Run all linters (black, isort, ruff)"
	@echo "  make format          Format code with black and isort"
	@echo "  make typecheck       Run mypy type checking"
	@echo "  make docs            Serve documentation locally"
	@echo "  make build           Build distribution packages"
	@echo "  make clean           Remove build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,cli,docs]"

test:
	pytest -v --cov=nostradamus_ioto_sdk --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

coverage:
	pytest --cov=nostradamus_ioto_sdk --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"
	@echo "Open with: open htmlcov/index.html (macOS) or xdg-open htmlcov/index.html (Linux)"

lint:
	@echo "Running black..."
	black --check .
	@echo "Running isort..."
	isort --check-only .
	@echo "Running ruff..."
	ruff check .

format:
	black .
	isort .

typecheck:
	mypy nostradamus_ioto_sdk

docs:
	mkdocs serve

build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

all: format lint typecheck test

ci: lint typecheck test
