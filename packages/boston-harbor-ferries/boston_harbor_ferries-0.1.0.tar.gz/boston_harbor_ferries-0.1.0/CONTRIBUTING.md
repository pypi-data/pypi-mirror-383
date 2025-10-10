# Contributing to Boston Harbor Ferries

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`
- `gmake` (FreeBSD/macOS) or `make` (Linux)
- APRS.fi API key (free from https://aprs.fi)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/aygp-dr/boston-harbor-ferries.git
cd boston-harbor-ferries

# Setup environment
gmake setup          # Creates venv, installs deps, creates .env
gmake .env          # Or just create .env if you prefer

# Edit .env and add your API key
# APRS_API_KEY=your-key-here

# Activate environment (optional if using uv)
source .venv/bin/activate

# Or use direnv
direnv allow
```

### Development Commands

```bash
# Run the tracker
gmake run                    # Track all ferries
uv run python -m boston_harbor_ferries.cli track 368157410  # Track specific

# Testing
gmake test                   # Run tests
gmake lint                   # Run linters (ruff, mypy)

# Code generation (optional)
gmake codegen-validate       # Validate OpenAPI spec
gmake codegen                # Generate client from spec
gmake codegen-clean          # Remove generated code

# Cleanup
gmake clean                  # Remove build artifacts
```

## Project Structure

```
boston-harbor-ferries/
├── boston_harbor_ferries/   # Main package
│   ├── cli.py              # CLI commands
│   ├── client.py           # APRS.fi HTTP client
│   ├── config.py           # Settings/configuration
│   ├── vessels.py          # Ferry database
│   ├── schemas.py          # Pydantic models
│   └── mcp_server.py       # MCP server
│
├── specs/                   # OpenAPI specifications
│   ├── aprs-fi-api.yaml    # API spec
│   └── architecture.md     # Architecture docs
│
├── scripts/                 # Utility scripts
│   └── analyze_ferry_history.py  # Data analysis
│
├── tests/                   # Test suite
├── .github/workflows/       # CI/CD
└── pyproject.toml          # Project metadata
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Follow existing code style (we use `ruff` for linting)
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

### 3. Run Tests

```bash
# Run all tests
gmake test

# Run linters
gmake lint

# Fix lint issues
uv run ruff check --fix boston_harbor_ferries/
```

### 4. Commit with Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

git commit -m "feat(cli): add route visualization command"
git commit -m "fix(client): handle null speed values"
git commit -m "docs: update API documentation"
git commit -m "test: add ferry position tests"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Adding a New Ferry

To add a new ferry to the tracker:

1. Find the vessel MMSI number (from Marine Traffic, VesselFinder, etc.)
2. Add to `boston_harbor_ferries/vessels.py`:

```python
VESSELS: dict[str, Vessel] = {
    # ... existing vessels ...
    "368XXXXXX": Vessel(
        name="NEW FERRY NAME",
        mmsi="368XXXXXX",
        route="Route Name",
        operator="Seaport Ferry",  # or "MBTA"
        capacity=90,
        description="Route description",
    ),
}
```

3. Test tracking:
```bash
uv run python -m boston_harbor_ferries.cli track 368XXXXXX
```

4. Update README.md with new ferry info

## Code Style

### Python

- Use type hints for all functions
- Follow PEP 8 (enforced by `ruff`)
- Maximum line length: 100 characters
- Use docstrings for public functions

```python
def get_vessel_position(mmsi: str, use_cache: bool = True) -> FerryPosition | None:
    """Get current position for a vessel by MMSI.

    Args:
        mmsi: Vessel MMSI number
        use_cache: Whether to use cached data if available

    Returns:
        FerryPosition if found, None otherwise
    """
    ...
```

### Commits

- Use conventional commits format
- Write descriptive commit messages
- Reference issues when applicable: `fix(client): handle timeout (#42)`

## Testing

### Writing Tests

Tests go in the `tests/` directory:

```python
# tests/test_client.py
import pytest
from boston_harbor_ferries.client import APRSClient

def test_vessel_position():
    with APRSClient() as client:
        pos = client.get_vessel_position("368157410")
        if pos:  # May not have data
            assert pos.mmsi == "368157410"
            assert -180 <= pos.longitude <= 180
            assert -90 <= pos.latitude <= 90
```

### Running Tests

```bash
# All tests
gmake test

# Specific test file
uv run pytest tests/test_client.py -v

# With coverage
uv run pytest --cov=boston_harbor_ferries tests/
```

## Publishing (Maintainers Only)

### PyPI Publishing

Publishing is automated via GitHub Actions when a release is created.

**Manual publish (if needed):**

```bash
# Build package
python -m build

# Check build
twine check dist/*

# Publish to TestPyPI (testing)
twine upload --repository testpypi dist/*

# Publish to PyPI (production)
gmake publish
```

### Creating a Release

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Commit: `git commit -m "chore: bump version to X.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. GitHub Actions will automatically publish to PyPI

## API Keys and Secrets

### For Development
- Get API key from https://aprs.fi (free registration)
- Add to `.env` file (gitignored)
- Never commit API keys!

### For CI/CD
- API keys stored as GitHub Secrets
- Access via `${{ secrets.APRS_API_KEY }}`
- Set in repository settings

## OpenAPI Spec Updates

If you modify the APRS.fi client schema:

1. Update `specs/aprs-fi-api.yaml`
2. Validate: `gmake codegen-validate`
3. Regenerate (optional): `gmake codegen`
4. Document changes in PR

## Documentation

- Update README.md for user-facing changes
- Update specs/architecture.md for design changes
- Add docstrings to all public functions
- Keep comments concise and meaningful

## Getting Help

- 📖 Read the [README](README.md)
- 🏗️ Check [Architecture docs](specs/architecture.md)
- 🐛 [Open an issue](https://github.com/aygp-dr/boston-harbor-ferries/issues)
- 💬 Ask in pull request discussions

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Recognition

Contributors will be recognized in:
- Git commit history
- GitHub contributors page
- Release notes (for significant contributions)

Thank you for contributing! 🚢
