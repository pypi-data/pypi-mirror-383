# Quick Start: Automated Releases with Semantic Release

## 🎯 Goal
Automatically publish to PyPI when you push to `main` branch with proper commit messages.

## 📋 Prerequisites Checklist

- [ ] GitHub account with repo access
- [ ] PyPI account ([Register here](https://pypi.org/account/register/))
- [ ] Git remote configured: `git remote -v` shows your repo

## 🚀 Setup Steps (5 minutes)

### Step 1: First Manual Publish (One-Time)

This claims the `futunn-helper` name on PyPI:

```bash
# 1. Build the package
cd /path/to/futunn-helper
uv build

# 2. Get temporary PyPI token
# Visit: https://pypi.org/manage/account/token/
# - Name: "temp-token"
# - Scope: "Entire account" (first time only)
# - Copy the token (starts with pypi-...)

# 3. Publish first version
uv publish --token pypi-YOUR-TEMP-TOKEN-HERE

# 4. Verify at https://pypi.org/project/futunn-helper/

# 5. Delete temp token at https://pypi.org/manage/account/token/
```

### Step 2: Configure PyPI Trusted Publishing

Visit: https://pypi.org/manage/project/futunn-helper/settings/publishing/

Click **"Add a new publisher"** and fill in:

```
PyPI Project Name:  futunn-helper
Owner:             yourusername          ← YOUR GitHub username
Repository:        futunn-helper
Workflow:          semantic-release.yml
Environment:       pypi
```

Click **"Add"**.

✅ **No tokens needed after this!**

### Step 3: Create GitHub Environment

Visit: `https://github.com/yourusername/futunn-helper/settings/environments`

1. Click **"New environment"**
2. Name: `pypi`
3. Click **"Configure environment"**
4. (Optional) Add protection rules for safety

### Step 4: Update Workflow File

Edit `.github/workflows/semantic-release.yml` line 22:

```yaml
if: github.repository_owner == 'yourusername'  # ← Change this
```

Replace `yourusername` with your actual GitHub username.

### Step 5: Push a Test Commit

```bash
# Make a change
echo "# Test" >> README.md

# Commit with conventional format
git add README.md
git commit -m "docs: add test documentation"

# Push to main
git push origin main

# Watch the workflow
gh run watch
# Or visit: https://github.com/yourusername/futunn-helper/actions
```

## 🎉 Done! Automated Releases Active

### How to Release New Versions

```bash
# Feature (0.1.0 → 0.2.0)
git commit -m "feat: add new market support"
git push

# Bug fix (0.1.0 → 0.1.1)
git commit -m "fix: handle connection timeout"
git push

# Breaking change (0.1.0 → 1.0.0)
git commit -m "feat!: change API interface

BREAKING CHANGE: removed deprecated methods"
git push
```

**That's it!** Semantic Release will:
1. Analyze commits
2. Bump version in `pyproject.toml`
3. Generate `CHANGELOG.md`
4. Create Git tag
5. Create GitHub Release
6. Publish to PyPI

## 📖 Full Documentation

- **Commit Message Guide**: See `SEMANTIC_RELEASE.md`
- **Secret Setup Details**: See `SETUP_SECRETS.md`
- **Troubleshooting**: See `SETUP_SECRETS.md` → Common Issues

## 🆘 Quick Troubleshooting

### No release created?
```bash
# Check commit message format
git log -1 --pretty=%B

# Must start with: feat, fix, perf, docs, chore, etc.
# Example: "feat: add new feature"
```

### PyPI publish failed?
```bash
# 1. Check PyPI trusted publisher settings
# Owner must match your GitHub username exactly

# 2. Check GitHub environment name is "pypi"
# Visit: https://github.com/yourusername/futunn-helper/settings/environments

# 3. Check workflow has id-token permission
# Should see: permissions.id-token = write
```

### Workflow doesn't run?
```bash
# Check Actions are enabled
# Visit: https://github.com/yourusername/futunn-helper/settings/actions

# Check you pushed to main branch
git branch --show-current  # Should show "main"
```

## 🔄 Alternative: Use Manual Token

If Trusted Publishing doesn't work, use manual token instead:

```bash
# 1. Create PyPI token
# Visit: https://pypi.org/manage/account/token/
# Scope: "Project: futunn-helper"

# 2. Add to GitHub secrets
# Visit: https://github.com/yourusername/futunn-helper/settings/secrets/actions
# Name: PYPI_API_TOKEN
# Value: pypi-your-token-here

# 3. Update workflow line 52
# Change: run: uv publish
# To:     run: uv publish --token ${{ secrets.PYPI_API_TOKEN }}
```

See `SETUP_SECRETS.md` for detailed manual token setup.

## 📚 Configuration Files

This setup uses:
- ✅ `pyproject.toml` - Version and semantic-release config
- ✅ `.releaserc.json` - Semantic release plugins (optional)
- ✅ `.github/workflows/semantic-release.yml` - GitHub Actions workflow
- ✅ `.github/workflows/release.yml` - Manual tag-based release (backup)

## 🎯 Summary

**One-time setup:**
1. Manual publish first version → Claims PyPI name
2. Configure Trusted Publisher → Links GitHub to PyPI
3. Create GitHub environment → Enables secure publishing
4. Update workflow file → Use your username

**Ongoing usage:**
```bash
git commit -m "feat: description"  # Feature
git commit -m "fix: description"   # Bug fix
git push                           # Auto-release!
```

**Zero maintenance** - No tokens to rotate, no secrets to manage.
