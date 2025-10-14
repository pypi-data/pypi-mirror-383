# GitHub Repository Secrets Setup Guide

This guide shows you how to set up repository secrets for automated PyPI publishing.

## Overview

The semantic-release workflow requires these secrets:
1. **`GITHUB_TOKEN`** - Automatically provided by GitHub (no setup needed)
2. **`PYPI_API_TOKEN`** - For publishing to PyPI (manual setup required)

## Option 1: PyPI Trusted Publishing (Recommended - No Token Needed)

**Advantages:**
- ✅ No secrets to manage
- ✅ More secure (short-lived OIDC tokens)
- ✅ No token rotation needed
- ✅ GitHub Actions native

**Setup Steps:**

### 1. Create PyPI Account
```bash
# Visit https://pypi.org/account/register/
# Verify your email
```

### 2. Register Project Name (First Time Only)
```bash
# Build package locally first
uv build

# Manually publish first version to claim the name
# Create API token temporarily at: https://pypi.org/manage/account/token/
uv publish --token pypi-your-temp-token-here

# Delete the temp token after first publish
```

### 3. Configure Trusted Publisher on PyPI
Visit: https://pypi.org/manage/project/futunn-helper/settings/publishing/

Click **"Add a new publisher"** and fill in:

| Field | Value |
|-------|-------|
| **PyPI Project Name** | `futunn-helper` |
| **Owner** | `yourusername` (your GitHub username) |
| **Repository name** | `futunn-helper` |
| **Workflow name** | `semantic-release.yml` |
| **Environment name** | `pypi` |

Click **"Add"**.

### 4. Create GitHub Environment
Go to: `https://github.com/yourusername/futunn-helper/settings/environments`

1. Click **"New environment"**
2. Name: `pypi`
3. (Optional) Add protection rules:
   - ✅ Required reviewers
   - ✅ Wait timer
4. Click **"Configure environment"**

### 5. Done!
No secrets needed. The workflow uses OIDC tokens automatically.

---

## Option 2: Manual PyPI Token (Alternative)

**Use this if:**
- Trusted Publishing is not available
- You need more control over tokens

### 1. Create PyPI API Token

Visit: https://pypi.org/manage/account/token/

1. Click **"Add API token"**
2. **Token name**: `futunn-helper-github-actions`
3. **Scope**: 
   - First time: "Entire account" (to create the project)
   - After first publish: "Project: futunn-helper" (more secure)
4. Click **"Add token"**
5. **Copy the token** - it starts with `pypi-`
   ```
   pypi-AgEIcHlwaS5vcmc...
   ```
6. ⚠️ **Save it now** - you can't see it again!

### 2. Add Token to GitHub Secrets

Go to: `https://github.com/yourusername/futunn-helper/settings/secrets/actions`

1. Click **"New repository secret"**
2. **Name**: `PYPI_API_TOKEN`
3. **Value**: Paste your `pypi-...` token
4. Click **"Add secret"**

### 3. Update Workflow File

Edit `.github/workflows/semantic-release.yml`:

```yaml
- name: Publish to PyPI (Manual Token)
  if: steps.release.outputs.released == 'true'
  run: uv publish --token ${{ secrets.PYPI_API_TOKEN }}
```

---

## Verification

### Check Secrets Are Set
```bash
# GitHub Token (automatic)
gh secret list
# Should NOT show GITHUB_TOKEN (it's automatic)

# PyPI Token (if using Option 2)
gh secret list
# Should show: PYPI_API_TOKEN
```

### Test Locally (Dry Run)
```bash
# Install GitHub CLI
brew install gh  # macOS
# or: https://cli.github.com/

# Login
gh auth login

# Test semantic-release (doesn't publish)
uv run semantic-release version --print

# Test build
uv build

# Test PyPI connection (TestPyPI first)
uv publish --repository testpypi --token pypi-test-token
```

### Test on GitHub Actions
```bash
# Make a commit
git add .
git commit -m "feat: test semantic-release setup"
git push

# Watch workflow
gh run watch

# Or visit:
# https://github.com/yourusername/futunn-helper/actions
```

---

## Common Issues

### Issue: `uv publish` fails with "401 Unauthorized"

**Solution for Trusted Publishing:**
```bash
# 1. Verify environment name matches
#    Workflow: environment.name = "pypi"
#    PyPI: Environment name = "pypi"

# 2. Check PyPI trusted publisher settings
#    Repository: yourusername/futunn-helper ✓
#    Workflow: semantic-release.yml ✓
#    Environment: pypi ✓

# 3. Ensure workflow has correct permissions
permissions:
  id-token: write  # Required for OIDC
  contents: write
```

**Solution for Manual Token:**
```bash
# 1. Check secret name exactly matches
echo '${{ secrets.PYPI_API_TOKEN }}'  # Check in workflow

# 2. Regenerate token on PyPI
# Visit: https://pypi.org/manage/account/token/

# 3. Update secret on GitHub
# Visit: https://github.com/yourusername/futunn-helper/settings/secrets/actions
```

### Issue: `semantic-release` doesn't create release

**Check commit message format:**
```bash
# ❌ Wrong
git commit -m "added new feature"

# ✅ Correct
git commit -m "feat: add new feature"

# View recent commits
git log --oneline -10
```

**Valid commit types:**
- `feat:` - New feature (minor version bump)
- `fix:` - Bug fix (patch version bump)
- `perf:` - Performance (patch version bump)
- `docs:` - Documentation (no bump)
- `chore:` - Maintenance (no bump)

### Issue: GitHub Actions workflow doesn't trigger

**Check:**
```bash
# 1. Is push to main branch?
git branch --show-current

# 2. Check workflow file exists
ls -la .github/workflows/semantic-release.yml

# 3. Check Actions are enabled
# Visit: https://github.com/yourusername/futunn-helper/settings/actions
```

### Issue: Permission denied errors

**Fix workflow permissions:**

Edit `.github/workflows/semantic-release.yml`:
```yaml
permissions:
  contents: write      # For pushing tags and commits
  issues: write        # For release notes
  pull-requests: write # For release PRs
  id-token: write      # For trusted publishing (OIDC)
```

---

## Security Best Practices

### ✅ DO
- Use Trusted Publishing (Option 1) when possible
- Use project-scoped tokens, not account-scoped
- Rotate tokens annually
- Use GitHub Environments for production deployments
- Enable 2FA on PyPI account
- Use `CODEOWNERS` file for release approval

### ❌ DON'T
- Don't commit tokens to git
- Don't use account-wide tokens (use project-scoped)
- Don't share tokens between projects
- Don't store tokens in plaintext
- Don't skip 2FA

---

## Advanced: Multiple Environments

For staging + production releases:

**PyPI TestPyPI (Staging):**
```yaml
# .github/workflows/semantic-release-test.yml
environment:
  name: testpypi
  url: https://test.pypi.org/project/futunn-helper/

- name: Publish to TestPyPI
  run: uv publish --repository testpypi
```

**PyPI Production:**
```yaml
# .github/workflows/semantic-release.yml
environment:
  name: pypi
  url: https://pypi.org/project/futunn-helper/

- name: Publish to PyPI
  run: uv publish
```

Configure both on PyPI:
- https://test.pypi.org/manage/project/futunn-helper/settings/publishing/
- https://pypi.org/manage/project/futunn-helper/settings/publishing/

---

## Quick Reference Commands

```bash
# Check secrets
gh secret list

# Set secret manually
gh secret set PYPI_API_TOKEN

# View workflow runs
gh run list --workflow=semantic-release.yml

# View specific run
gh run view

# Re-run failed workflow
gh run rerun

# Check PyPI package
uv pip index versions futunn-helper

# Test package install
uv pip install futunn-helper
```

---

## Resources

- **PyPI Trusted Publishing**: https://docs.pypi.org/trusted-publishers/
- **GitHub Environments**: https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment
- **GitHub Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **UV Publishing**: https://docs.astral.sh/uv/guides/publish/
- **Semantic Release**: https://python-semantic-release.readthedocs.io/

---

## Summary

**Recommended Setup (Trusted Publishing):**
1. ✅ Build and manually publish first version to PyPI
2. ✅ Configure Trusted Publisher on PyPI (no token needed)
3. ✅ Create `pypi` environment on GitHub
4. ✅ Push conventional commits to main
5. ✅ Automated releases work via OIDC

**Alternative Setup (Manual Token):**
1. ✅ Create PyPI API token
2. ✅ Add `PYPI_API_TOKEN` to GitHub secrets
3. ✅ Update workflow to use token
4. ✅ Push conventional commits to main
5. ✅ Automated releases work via token

Both methods work - Trusted Publishing is more secure and maintenance-free.
