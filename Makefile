.PHONY: help install install-dev test lint format type-check build clean docs

help:
	@echo "Available commands:"
	@echo "  install      Install package in development mode"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  type-check   Run type checking"
	@echo "  build        Build package"
	@echo "  build-exe    Build standalone executable"
	@echo "  clean        Clean build artifacts"
	@echo "  docs         Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e .[dev]
	pip install -r requirements-dev.txt

test:
	pytest

test-cov:
	pytest --cov=vscode_sync --cov-report=html --cov-report=term

lint:
	flake8 vscode_sync tests
	black --check vscode_sync tests
	isort --check-only vscode_sync tests

format:
	black vscode_sync tests
	isort vscode_sync tests

type-check:
	mypy vscode_sync

build:
	python -m build

build-exe:
	python scripts/build.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	sphinx-build -b html docs docs/_build/html

release: clean build
	twine upload dist/*

dev-setup: install-dev
	pre-commit install
