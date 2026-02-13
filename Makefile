.PHONY: help install install-dev test test-unit test-integration coverage lint format typecheck pylint docs clean build ci

help:
	@echo "Available commands:"
	@echo ""
	@echo "  Setup:"
	@echo "    make install           Install package in production mode"
	@echo "    make install-dev       Install package with dev dependencies"
	@echo ""
	@echo "  Testing:"
	@echo "    make test              Run all tests with coverage"
	@echo "    make test-unit         Run unit tests only"
	@echo "    make test-integration  Run integration tests only"
	@echo "    make coverage          Run tests and generate HTML coverage report"
	@echo ""
	@echo "  Code Quality:"
	@echo "    make format            Format code with black and isort"
	@echo "    make lint              Run all linters (black, isort, ruff, pylint)"
	@echo "    make typecheck         Run mypy type checking"
	@echo "    make pylint            Run pylint only"
	@echo ""
	@echo "  CI:"
	@echo "    make ci                Run full CI pipeline (lint + typecheck + test + coverage threshold)"
	@echo ""
	@echo "  Other:"
	@echo "    make docs              Serve documentation locally"
	@echo "    make build             Build distribution packages"
	@echo "    make clean             Remove build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,cli,docs]"

test:
	pytest -v --cov=nostradamus_ioto_sdk --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

coverage:
	pytest --cov=nostradamus_ioto_sdk --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"
	@echo "Open with: xdg-open htmlcov/index.html (Linux) or open htmlcov/index.html (macOS)"

format:
	black .
	isort .

lint:
	@echo "==> black (check)"
	black --check .
	@echo "==> isort (check)"
	isort --check-only .
	@echo "==> ruff"
	ruff check .
	@echo "==> pylint"
	pylint nostradamus_ioto_sdk

typecheck:
	mypy nostradamus_ioto_sdk

pylint:
	pylint nostradamus_ioto_sdk

docs:
	mkdocs serve

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .mypy_cache htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ci:
	@echo "========================================"
	@echo "  CI Pipeline"
	@echo "========================================"
	@echo ""
	@echo "[1/5] Formatting check (black + isort)"
	@echo "----------------------------------------"
	black --check .
	isort --check-only .
	@echo ""
	@echo "[2/5] Linting (ruff)"
	@echo "----------------------------------------"
	ruff check .
	@echo ""
	@echo "[3/5] Linting (pylint)"
	@echo "----------------------------------------"
	pylint nostradamus_ioto_sdk
	@echo ""
	@echo "[4/5] Type checking (mypy)"
	@echo "----------------------------------------"
	mypy nostradamus_ioto_sdk
	@echo ""
	@echo "[5/5] Tests + coverage (pytest, threshold: 80%)"
	@echo "----------------------------------------"
	pytest -v --cov=nostradamus_ioto_sdk --cov-report=term-missing --cov-fail-under=80
	@echo ""
	@echo "========================================"
	@echo "  CI Pipeline: ALL CHECKS PASSED"
	@echo "========================================"
