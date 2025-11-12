# Releasing `op-opsdevnz`

This repository publishes to TestPyPI first, then PyPI once smoke tests pass.

## Prerequisites

- Access to the `startmeup-nz` TestPyPI / PyPI tokens (stored in 1Password).
- `twine` and `build` are installed via `pip install -e .[dev]`.
- You are on a clean `main` branch with CI green.

## Workflow

1. **Bump the Version**
   - Update `project.version` inside `pyproject.toml`.
   - Update any version references in documentation if needed.
2. **Changelog**
   - Summarise the release in `README.md` or a future `CHANGELOG.md`.
3. **Tests**
   ```bash
   ruff check src tests
   mypy src
   pytest --color=yes --durations=10
   ```
4. **Build the Distribution**
   ```bash
   rm -rf dist/
   python -m build
   ```
5. **Publish to TestPyPI**
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
   - Try installing it with
     ```bash
     pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple op-opsdevnz
     ```
6. **Tag + Push**
   ```bash
   git tag v0.1.1
   git push origin main v0.1.1
   ```
7. **PyPI (optional for now)**
   - Repeat step 5 with `--repository pypi` once TestPyPI validation passes.

## CI/CD

GitHub Actions runs lint, type-checking, tests, and a build on every push and
pull request, so releases should only require the manual TestPyPI upload plus a
tag.
