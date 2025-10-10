# Makefile for Boston Harbor Ferries
# Use gmake on FreeBSD

# Use uv to run Python commands
PYTHON := uv run python

.PHONY: help install test lint clean .env setup dev codegen codegen-validate publish publish-test

# Default target
help:
	@echo "Boston Harbor Ferries - Available targets:"
	@echo "  make setup      - Complete project setup (venv + deps + .env)"
	@echo "  make .env       - Create .env from .env.example"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Install development dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make clean      - Remove build artifacts and cache"
	@echo "  make run        - Run CLI tracker"
	@echo ""
	@echo "Code Generation:"
	@echo "  make codegen-validate  - Validate OpenAPI spec"
	@echo "  make codegen           - Generate Python client from OpenAPI spec"
	@echo "  make codegen-clean     - Remove generated code"
	@echo ""
	@echo "Publishing (Maintainers):"
	@echo "  make publish-test      - Publish to TestPyPI"
	@echo "  make publish           - Publish to PyPI (use with caution!)"

# Create .env from .env.example if it doesn't exist
.env:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "✓ .env created - please update with your API key"; \
	else \
		echo "✓ .env already exists"; \
	fi

# Complete setup: venv + dependencies + .env
setup: .env
	@echo "Setting up virtual environment..."
	@python3 -m venv .venv
	@echo "Installing dependencies..."
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install -e .
	@echo "✓ Setup complete!"
	@echo "  Run: source .venv/bin/activate"
	@echo "  Or use direnv: direnv allow"

# Install production dependencies
install:
	pip install -e .

# Install development dependencies
dev:
	pip install -e ".[dev]"

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v

# Run linters
lint:
	$(PYTHON) -m ruff check boston_harbor_ferries/
	$(PYTHON) -m mypy boston_harbor_ferries/

# Clean build artifacts and cache
clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf __pycache__/ .pytest_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Run the CLI tracker
run:
	@if [ ! -f .env ]; then \
		echo "Error: .env not found. Run 'gmake .env' first."; \
		exit 1; \
	fi
	$(PYTHON) -m boston_harbor_ferries.cli track-all

# Code Generation Targets

# Validate OpenAPI spec
codegen-validate:
	@echo "Validating OpenAPI specification..."
	@if command -v npx > /dev/null; then \
		npx @redocly/cli lint specs/aprs-fi-api.yaml; \
	else \
		echo "⚠️  Redocly CLI not found. Install: npm install -g @redocly/cli"; \
		echo "   Skipping validation..."; \
	fi

# Generate Python client from OpenAPI spec
codegen: codegen-validate
	@echo "Generating Python client from OpenAPI spec..."
	@mkdir -p generated
	@if command -v openapi-python-client > /dev/null; then \
		openapi-python-client generate \
			--path specs/aprs-fi-api.yaml \
			--output-path generated/aprs-fi-client \
			--config specs/codegen-config.yaml && \
		echo "✓ Client generated in generated/aprs-fi-client/"; \
	else \
		echo "❌ openapi-python-client not found."; \
		echo "   Install: pip install openapi-python-client"; \
		echo ""; \
		echo "Alternative: Use openapi-generator-cli"; \
		echo "   npm install -g @openapitools/openapi-generator-cli"; \
		echo "   openapi-generator-cli generate -i specs/aprs-fi-api.yaml -g python -o generated/aprs-fi-client"; \
		exit 1; \
	fi

# Clean generated code
codegen-clean:
	@echo "Removing generated code..."
	@rm -rf generated/
	@echo "✓ Generated code removed"

# Publishing Targets

# Build package
build:
	@echo "Building package..."
	@rm -rf dist/ build/ *.egg-info
	@python -m build
	@echo "✓ Package built in dist/"

# Publish to TestPyPI (for testing)
publish-test: build
	@echo "Publishing to TestPyPI..."
	@twine check dist/*
	@twine upload --repository testpypi dist/*
	@echo "✓ Published to TestPyPI"
	@echo "  Test install: pip install --index-url https://test.pypi.org/simple/ boston-harbor-ferries"

# Publish to PyPI (production)
publish: build
	@echo "⚠️  Publishing to PyPI (PRODUCTION)..."
	@echo "   This will make the package publicly available!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		twine check dist/*; \
		twine upload dist/*; \
		echo "✓ Published to PyPI"; \
		echo "  Install: pip install boston-harbor-ferries"; \
	else \
		echo "Cancelled."; \
	fi
