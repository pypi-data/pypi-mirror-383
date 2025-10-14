# Semantic Release Setup for futunn-helper

## Overview

This project uses **Python Semantic Release** for automated versioning and releases based on conventional commits.

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature (triggers minor version bump: 0.1.0 → 0.2.0)
- **fix**: Bug fix (triggers patch version bump: 0.1.0 → 0.1.1)
- **perf**: Performance improvement (triggers patch version bump)
- **docs**: Documentation changes (no version bump)
- **style**: Code style changes (no version bump)
- **refactor**: Code refactoring (no version bump)
- **test**: Test changes (no version bump)
- **build**: Build system changes (no version bump)
- **ci**: CI configuration changes (no version bump)
- **chore**: Other changes (no version bump)

### Breaking Changes

Add `BREAKING CHANGE:` in the footer or `!` after type to trigger major version bump:

```
feat!: remove deprecated get_stock_list_sync method

BREAKING CHANGE: Synchronous methods have been removed. Use async methods only.
```

This triggers: 0.1.0 → 1.0.0

### Examples

```bash
# Feature (0.1.0 → 0.2.0)
git commit -m "feat(client): add support for Singapore market"

# Bug fix (0.1.0 → 0.1.1)
git commit -m "fix(token): handle expired CSRF tokens correctly"

# Performance (0.1.0 → 0.1.1)
git commit -m "perf(client): reduce API call latency with connection pooling"

# Breaking change (0.1.0 → 1.0.0)
git commit -m "feat(api)!: change market_type parameter to market_code

BREAKING CHANGE: market_type integer replaced with market_code string"

# No release
git commit -m "docs: update README with new examples"
git commit -m "chore: update dependencies"
```

## How It Works

1. **On every push to `main` branch**, the semantic-release workflow runs
2. Analyzes commits since last release
3. Determines version bump (major/minor/patch)
4. Updates version in `pyproject.toml`
5. Generates/updates `CHANGELOG.md`
6. Creates Git tag and GitHub release
7. Publishes to PyPI via Trusted Publishing

## Configuration

Located in `pyproject.toml`:

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
branch = "main"
build_command = "uv build"
commit_message = "chore: release v{version}"
```

## Manual Release (Local)

```bash
# Dry run (see what would happen)
uv run semantic-release version --no-commit --no-tag --no-push

# Perform release
uv run semantic-release version

# Publish to PyPI
uv run semantic-release publish
```

## GitHub Setup

### 1. Enable GitHub Actions

Ensure Actions are enabled in repository settings.

### 2. Configure PyPI Trusted Publishing

- Visit: https://pypi.org/manage/project/futunn-helper/settings/publishing/
- Add trusted publisher:
  - **Owner**: Your GitHub username/org
  - **Repository**: `futunn-helper`
  - **Workflow**: `semantic-release.yml`
  - **Environment**: `pypi`

### 3. Create GitHub Environment (Optional)

For additional protection:
- Settings → Environments → New environment
- Name: `pypi`
- Add protection rules (e.g., required reviewers)

## Workflow Files

- `.github/workflows/semantic-release.yml` - Automated releases on push to main
- `.github/workflows/release.yml` - Manual releases via Git tags (kept as backup)

## Version History

All versions are tracked in:
- `CHANGELOG.md` - Auto-generated changelog
- GitHub Releases - Created automatically
- PyPI - Published packages
- Git tags - Version markers

## Tips

### Multiple Changes

If you have multiple commits, the highest version bump applies:

```bash
git commit -m "docs: update README"      # No bump
git commit -m "fix: handle timeout"      # Patch (0.1.0 → 0.1.1)
git commit -m "feat: add new endpoint"   # Minor wins (0.1.0 → 0.2.0)
git push
# Result: 0.1.0 → 0.2.0
```

### Skip Release

Use `[skip ci]` or `[skip release]` in commit message:

```bash
git commit -m "chore: update .gitignore [skip ci]"
```

### Revert Release

If a release has issues:

```bash
# Revert the commit
git revert HEAD

# Push (this creates a new patch release)
git push
```

## Troubleshooting

### No release created

- Check commit messages follow conventional format
- Ensure commits contain `feat`, `fix`, or `perf` types
- Check GitHub Actions logs for errors

### PyPI publish failed

- Verify Trusted Publishing is configured correctly
- Check PyPI environment name matches workflow (`pypi`)
- Ensure version doesn't already exist on PyPI

### Version conflicts

If local version differs from remote:

```bash
git fetch --tags
git pull --rebase
```

## Migration from Manual Releases

If you were using manual tags (`v0.1.0`):

1. Keep existing `.github/workflows/release.yml` for backup
2. Use `semantic-release.yml` for automated releases
3. Stop creating manual tags
4. Commit using conventional format
5. Push to main - semantic-release handles the rest

## Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Semantic Release Docs](https://python-semantic-release.readthedocs.io/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)
