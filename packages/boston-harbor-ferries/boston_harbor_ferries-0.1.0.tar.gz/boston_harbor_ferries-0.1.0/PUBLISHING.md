# Publishing boston-harbor-ferries to PyPI

Quick reference for publishing the package to PyPI.

## Prerequisites

- Maintainer access to https://github.com/aygp-dr/boston-harbor-ferries
- PyPI account at https://pypi.org
- Trusted publisher configured (see `.github/PYPI_SETUP.md`)

## Quick Start: Automated Publishing

### 1. Update Version

Edit `pyproject.toml`:
```toml
[project]
name = "boston-harbor-ferries"
version = "0.2.0"  # ← Update this
```

### 2. Create Release

```bash
# Commit version bump
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"
git push

# Create and push tag
git tag v0.2.0
git push origin v0.2.0
```

### 3. Publish via GitHub

1. Go to: https://github.com/aygp-dr/boston-harbor-ferries/releases
2. Click "Draft a new release"
3. Choose tag: `v0.2.0`
4. Generate release notes or write manually
5. Click "Publish release"

GitHub Actions will automatically:
- Build the package
- Run checks
- Publish to PyPI

## Manual Publishing

If you need to publish locally:

```bash
# Test build
python -m build
twine check dist/*

# Publish to TestPyPI (testing)
gmake publish-test

# Publish to PyPI (production)
gmake publish
```

## PyPI Trusted Publisher Setup

Values for https://pypi.org/manage/account/publishing/:

| Field | Value |
|-------|-------|
| PyPI Project Name | `boston-harbor-ferries` |
| Owner | `aygp-dr` |
| Repository | `boston-harbor-ferries` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

**Full setup guide:** `.github/PYPI_SETUP.md`

## Verification

After publishing:

```bash
# Install from PyPI
pip install boston-harbor-ferries

# Verify version
python -c "import boston_harbor_ferries; print(boston_harbor_ferries.__version__)"

# Test CLI
harbor-ferry --version
harbor-ferry list-vessels
```

## Troubleshooting

**Build fails?**
```bash
gmake clean
python -m build
twine check dist/*
```

**Version conflict?**
- Can't reupload same version to PyPI
- Bump version in `pyproject.toml`
- PyPI versions are immutable

**Workflow fails?**
- Check GitHub Actions logs
- Verify trusted publisher settings
- Ensure environment `pypi` exists

## Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` (if exists)
- [ ] Run tests: `gmake test`
- [ ] Run linters: `gmake lint`
- [ ] Commit changes
- [ ] Create and push git tag
- [ ] Create GitHub Release
- [ ] Verify on PyPI
- [ ] Test install: `pip install boston-harbor-ferries`

## Version Strategy

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backwards compatible
- **PATCH** (0.1.1): Bug fixes

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature (ferry route)
- `0.1.0` → `1.0.0`: Breaking API change

## See Also

- Contributor Guide: `CONTRIBUTING.md`
- PyPI Setup Guide: `.github/PYPI_SETUP.md`
- Workflow: `.github/workflows/publish.yml`
