# PyPI Trusted Publishing Setup

This guide shows how to set up PyPI Trusted Publishing for automatic package releases.

## PyPI Trusted Publisher Configuration

Configure at: https://pypi.org/manage/account/publishing/

### Settings for boston-harbor-ferries

| Field | Value |
|-------|-------|
| **PyPI Project Name** | `boston-harbor-ferries` |
| **Owner** | `aygp-dr` |
| **Repository name** | `boston-harbor-ferries` |
| **Workflow name** | `publish.yml` |
| **Environment name** | `pypi` (optional but recommended) |

## Step-by-Step Setup

### 1. Register Package Name on PyPI (First Time Only)

**Option A: Via Web UI**
1. Go to https://pypi.org
2. Log in
3. Click "Your projects" → "Publishing"
4. Add pending publisher with values above
5. This reserves the name for your first publish

**Option B: First Manual Upload**
```bash
# Build package locally
python -m build

# Upload to reserve name (one-time)
twine upload dist/*
```

### 2. Configure Trusted Publisher on PyPI

1. Visit: https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher" (if project doesn't exist yet)
   OR "Add a new publisher" (if project exists)

3. Fill in:
   ```
   PyPI project name: boston-harbor-ferries
   Owner:            aygp-dr
   Repository:       boston-harbor-ferries
   Workflow:         publish.yml
   Environment:      pypi
   ```

4. Click "Add"

### 3. Create GitHub Environment (Recommended)

1. Go to: https://github.com/aygp-dr/boston-harbor-ferries/settings/environments
2. Click "New environment"
3. Name: `pypi`
4. Configure protection rules:
   - ✅ Required reviewers (optional - add maintainers)
   - ✅ Deployment branches: Selected branches → `main` only

### 4. Verify Workflow File

Check `.github/workflows/publish.yml` has:

```yaml
environment:
  name: pypi
  url: https://pypi.org/p/boston-harbor-ferries

permissions:
  id-token: write  # Required for trusted publishing
  contents: read
```

## Publishing Process

### Automatic (Recommended)

1. Update version in `pyproject.toml`
2. Commit changes
3. Create a GitHub Release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. Go to GitHub → Releases → "Draft a new release"
5. Choose tag `v0.1.0`
6. Click "Publish release"
7. GitHub Actions automatically publishes to PyPI

### Manual (Local)

```bash
# Build
gmake build

# Test on TestPyPI first
gmake publish-test

# Then publish to PyPI
gmake publish
```

## Verification

After publishing, verify at:
- Package page: https://pypi.org/project/boston-harbor-ferries/
- Install: `pip install boston-harbor-ferries`

## Troubleshooting

### Error: "Package not found"
- Ensure package is registered on PyPI first
- Check project name matches exactly

### Error: "Invalid or non-existent authentication"
- Verify trusted publisher settings on PyPI
- Check workflow file environment name matches
- Ensure `id-token: write` permission is set

### Error: "This filename has already been used"
- Version already published
- Bump version in `pyproject.toml`
- PyPI doesn't allow re-uploading same version

## No Secrets Needed!

With Trusted Publishing:
- ❌ No API tokens to manage
- ❌ No secrets to configure
- ✅ GitHub Actions OIDC handles authentication
- ✅ More secure than API tokens

## References

- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Publishing Action](https://github.com/pypa/gh-action-pypi-publish)
