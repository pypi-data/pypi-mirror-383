.PHONY: help install install-dev lint format check test test-verbose migrate makemigrations shell clean build

help:
	@echo "Django Issue Capture - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install runtime dependencies"
	@echo "  make install-dev    Install all dependencies (runtime + dev)"
	@echo ""
	@echo "Quality:"
	@echo "  make lint           Run ruff linter"
	@echo "  make format         Auto-format code with ruff"
	@echo "  make typecheck      Run mypy type checking"
	@echo "  make check          Run all quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run test suite"
	@echo "  make test-verbose   Run tests with verbose output"
	@echo ""
	@echo "Django:"
	@echo "  make migrate        Run migrations"
	@echo "  make makemigrations Create new migrations"
	@echo "  make shell          Django shell"
	@echo ""
	@echo "Package:"
	@echo "  make build          Build package"
	@echo "  make clean          Clean generated files"

install:
	uv sync

install-dev:
	uv sync --extra dev

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

check: lint typecheck test

test:
	PYTHONPATH=. uv run python tests/manage.py test

test-verbose:
	PYTHONPATH=. uv run python tests/manage.py test --verbosity=2

migrate:
	PYTHONPATH=. uv run python tests/manage.py migrate

makemigrations:
	PYTHONPATH=. uv run python tests/manage.py makemigrations django_issue_capture

shell:
	PYTHONPATH=. uv run python tests/manage.py shell

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .venv/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -f tests/test_db.sqlite3
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	uv build
