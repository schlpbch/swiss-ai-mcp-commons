# Deployment Guide: Swiss AI MCP Commons

This document outlines the deployment and publishing strategy for the swiss-ai-mcp-commons library across different environments and deployment targets.

## Current Status: Phase 1 - Git-Based Dependencies

**Active:** All MCPs currently use Git-based references to commons v1.0.0
```toml
swiss-ai-mcp-commons @ git+https://github.com/schlpbch/swiss-ai-mcp-commons.git@v1.0.0
```

**Why Git References?**
- Immediate resolution without requiring PyPI setup
- Works on FastMCP Cloud and other Git-capable environments
- Leverages existing GitHub infrastructure
- No API tokens needed for public repositories

**Affected MCPs:**
- mcp-travel-assistant (v3.0.0)
- swiss-tourism-mcp (v2.0.0)
- open-meteo-mcp (v3.0.0)
- aareguru-mcp (v3.0.0)

**Testing Status:**
- ✅ Travel Concierge: Dependency resolution verified
- ✅ Swiss Tourism: 36+ tests passing
- ✅ Open-Meteo: 125 tests passing
- ✅ Aareguru: 214 tests passing (2 skipped)

---

## Phase 2: PyPI Publishing (Next)

**Timeline:** This week (after current work)

### 2.1 PyPI Setup

#### Prerequisites
1. PyPI Account (if not already created)
   - Visit https://pypi.org/account/register/
   - Verify email address
   - Enable 2FA (recommended)

2. Create API Token
   - Login to PyPI
   - Navigate to Account Settings → API tokens
   - Create new token with scope "swiss-ai-mcp-commons"
   - Store securely (won't be shown again)

#### Store Token in GitHub Secrets
1. Go to commons repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste the PyPI token
5. Click "Add secret"

### 2.2 First Time Publishing

```bash
# Ensure you're on the latest master branch
git checkout master
git pull origin master

# Verify version is 1.0.0 in pyproject.toml
grep 'version = ' pyproject.toml

# Build locally to verify
python -m build

# Test upload to PyPI test environment (optional)
twine upload dist/* -r testpypi

# Upload to PyPI
twine upload dist/*
```

**Verification:**
- Check https://pypi.org/project/swiss-ai-mcp-commons/
- Package should appear within 1-2 minutes

### 2.3 Automatic Publishing via GitHub Actions

The workflow is already configured in `.github/workflows/publish.yml`:

**Triggers:**
- Publishing a GitHub release
- Pushing a version tag (v*.*)

**Publishing a Release:**
```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release swiss-ai-mcp-commons v1.0.0"

# Push tag
git push origin v1.0.0

# Or use GitHub web interface to create release
# → Releases → Draft a new release → Tag version v1.0.0 → Publish release
```

---

## Phase 3: Update MCPs to Use PyPI (Week After Phase 2)

Once confirmed published on PyPI, update all 4 MCPs:

### 3.1 Update Dependency References

**Travel Concierge** (`pyproject.toml`):
```toml
# Before
swiss-ai-mcp-commons @ git+https://github.com/schlpbch/swiss-ai-mcp-commons.git@v1.0.0

# After
swiss-ai-mcp-commons>=1.0.0,<2.0.0
```

**Swiss Tourism** (`pyproject.toml`):
```toml
# Before
swiss-ai-mcp-commons @ git+https://github.com/schlpbch/swiss-ai-mcp-commons.git@v1.0.0

# After
swiss-ai-mcp-commons>=1.0.0,<2.0.0
```

**Open-Meteo** (`pyproject.toml`):
```toml
# Before
swiss-ai-mcp-commons @ git+https://github.com/schlpbch/swiss-ai-mcp-commons.git@v1.0.0

# After
swiss-ai-mcp-commons>=1.0.0,<2.0.0
```

**Aareguru** (`pyproject.toml`):
```toml
# Before
swiss-ai-mcp-commons @ git+https://github.com/schlpbch/swiss-ai-mcp-commons.git@v1.0.0

# After
swiss-ai-mcp-commons>=1.0.0,<2.0.0
```

### 3.2 Verification Steps

For each MCP:
```bash
# Install with PyPI dependency
uv sync

# Run core tests
uv run pytest -q

# Verify commons is from PyPI
pip show swiss-ai-mcp-commons
```

### 3.3 Create Patch Release Commits

```bash
# For each MCP
git add pyproject.toml
git commit -m "chore: update commons dependency to PyPI version"
git push origin main

# Bump MCP versions if desired
# e.g., 3.0.0 → 3.0.1
```

---

## Environment-Specific Deployment

### Local Development
**Current:** Git references (file:// or @git+)
**Status:** ✅ Working
```bash
uv sync
uv run pytest
```

### FastMCP Cloud
**Current:** Git references work
**After PyPI:** Standard pip install will work
```bash
# Git references work immediately
# PyPI version will also work after Phase 3
```

### Docker Deployment
**Dockerfile Example:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies (will use PyPI version in Phase 3)
RUN pip install -e .

# Run MCP server
CMD ["python", "-m", "open_meteo_mcp.server"]
```

### CI/CD Pipelines
**GitHub Actions Example:**
```yaml
- name: Install MCP
  run: |
    pip install -e .
    # Will pull from PyPI once Phase 3 complete
```

---

## Versioning Strategy

### Commons Library Versions
- **1.0.0** (Current): Initial release with 11 shared models, HTTP client, logging
- **1.x.x** (Future): Backward-compatible updates (new models, minor features)
- **2.0.0** (Future): Breaking changes (model restructuring, API changes)

### MCP Update Strategy
When commons is updated:

**Patch Update (1.0.x):**
- No dependency pin changes needed
- Automatic via `>=1.0.0,<2.0.0`

**Minor Update (1.x):**
- New models or non-breaking features
- Requires MCP to explicitly use new models
- MCP can bump minor version (e.g., 3.0 → 3.1)

**Major Update (2.0.0):**
- Breaking changes to commons API
- MCPs must update to use new commons
- MCPs bump major version (e.g., 3.0 → 4.0)

---

## Rollback Plan

### If PyPI Publishing Fails

1. **Keep using Git references** (Phase 1 remains active)
2. **Fix the issue** (check publish workflow logs)
3. **Retry** via GitHub Actions or manual `twine upload`

### If MCPs Break After PyPI Migration

1. **Revert to Git references:**
   ```bash
   # In each MCP's pyproject.toml
   swiss-ai-mcp-commons @ git+https://github.com/schlpbch/swiss-ai-mcp-commons.git@v1.0.0
   ```

2. **Diagnose issue** (likely version mismatch or API change)

3. **Create hotfix** in commons if needed

---

## Monitoring & Maintenance

### PyPI Package Health
- Check download stats: https://libraries.io/pypi/swiss-ai-mcp-commons
- Monitor GitHub issues for dependency problems
- Track MCP compatibility matrix

### Version Compatibility Matrix

| Commons | Travel | Tourism | Meteo | Aareguru |
|---------|--------|---------|-------|----------|
| 1.0.0   | 3.0.0  | 2.0.0   | 3.0.0 | 3.0.0   |
| 1.0.1   | 3.0.x  | 2.0.x   | 3.0.x | 3.0.x   |
| 1.1.0   | 3.1.0  | 2.1.0   | 3.1.0 | 3.1.0   |

---

## Future Considerations

### 1. Conda Distribution
- Once stable, publish to conda-forge
- Enables installation via: `conda install swiss-ai-mcp-commons`

### 2. Documentation Site
- Build documentation with Sphinx or MkDocs
- Host on ReadTheDocs
- Link from PyPI project page

### 3. Security Scanning
- Enable Dependabot for automated dependency updates
- Set up code scanning for vulnerabilities
- Consider security policy in SECURITY.md

### 4. Community Contributions
- Set up contributor guidelines
- Create templates for issues/PRs
- Establish release process for community PRs

### 5. Automated Testing
- Set up test matrix for Python 3.9-3.12
- Test against multiple FastMCP versions
- Add integration tests with all dependent MCPs

---

## Questions & Troubleshooting

### Q: Why not publish to PyPI immediately?
**A:** Git references work out-of-the-box and don't require PyPI account setup. This gives time to verify everything works before publishing to the public PyPI registry.

### Q: What if I need to update commons while MCPs are using it?
**A:** With semver versioning:
- Bug fixes (1.0.0 → 1.0.1): Auto-used by MCPs
- Features (1.0.0 → 1.1.0): Requires MCP to opt-in
- Breaking changes (1.0.0 → 2.0.0): MCPs must explicitly migrate

### Q: How do I test PyPI locally?
**A:**
```bash
pip install twine
# Build and upload to test PyPI
twine upload --repository testpypi dist/*
# Install from test PyPI
pip install --index-url https://test.pypi.org/simple/ swiss-ai-mcp-commons
```

### Q: Can I unpublish from PyPI?
**A:** PyPI doesn't allow deletion of published versions (prevents dependency breakage). If you make a mistake:
1. Yank the problematic version: PyPI → Package → Release History → Actions → Yank
2. Upload corrected version with new semver number

---

## Next Steps

1. ✅ **Phase 1 Complete:** Git references working
2. ⏭️ **Phase 2 (Next):** Set up PyPI and publish commons
3. ⏭️ **Phase 3:** Update all MCPs to use PyPI version
4. ⏭️ **Phase 4:** Monitor and maintain package health

**Estimated Timeline:**
- Phase 2: 1-2 hours (setup + first publish)
- Phase 3: 30 minutes (update all 4 MCPs)
- Ongoing: Monitoring + maintenance as needed
