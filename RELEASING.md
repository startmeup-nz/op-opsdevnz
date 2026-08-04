# Releasing `op-opsdevnz`

All releases are automated through GitHub Actions and [Trusted Publishing
(OIDC)](https://docs.pypi.org/trusted-publishers/). No API tokens are stored
or managed — pushing a version tag triggers the pipeline.

## Conventions

| What | Rule |
|------|------|
| Versioning | [Semantic Versioning](https://semver.org) |
| Tag format | `v<version>` (e.g. `v0.2.0`) |
| Branch | `main` only — tags must point at a commit on `main` |
| Auth | Trusted Publishing (OIDC) — no API tokens |

## Prerequisites

- `uv` installed
- Clean `main` branch, CI green
- PyPI Trusted Publisher configured for the `pypi` environment on PyPI, and
  for the `testpypi` environment on TestPyPI

## Release Workflow

### 1. Prepare

On a branch off `main`:

```bash
# Bump version in pyproject.toml
version = "0.2.0"

# Move changelog entries from [Unreleased] to [0.2.0]
```

### 2. Merge and tag

```bash
git checkout main
git pull origin main
git tag -s v0.2.0 -m "v0.2.0"
git push origin v0.2.0
```

### 3. Watch CI

Pushing the tag fires `.github/workflows/publish.yml`:

| Job | What it does |
|-----|-------------|
| `verify` | Fails unless the tag matches `pyproject.toml`; runs ruff, mypy, pytest (with coverage threshold), builds the artifacts, `twine check`s them, and smoke-tests the built wheel in a clean venv |
| `test-pypi` | Publishes the verified artifacts to TestPyPI, installs from TestPyPI, and runs `op-opsdevnz --help` / `--version` |
| `pypi` | Runs only if `test-pypi` passes; publishes the same verified artifacts to PyPI |

### 4. Verify

```bash
pip install op-opsdevnz==0.2.0
op-opsdevnz --help
```

## Dry-run releases

To validate the pipeline without publishing to real PyPI, temporarily comment
out the `pypi` job in `.github/workflows/publish.yml`, tag and push, then
restore it after confirming TestPyPI succeeds.
