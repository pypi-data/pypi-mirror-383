.PHONY: format lint lint-check lint-check-unsafe test install dev-install clean

# Format code
format:
	uv run ruff format src/ tests/

# Lint and fix issues
lint:
	uv run ruff check src/ tests/ --fix

# Check linting without fixing
lint-check:
	uv run ruff check src/ 

# Check linting with unsafe fixes
lint-check-unsafe:
	uv run ruff check src/ --fix --unsafe-fixes

# Run tests
test:
	uv run pytest tests/

# Install the package
install:
	uv pip install .

# Install in development mode
dev-install:
	uv pip install -e .

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
