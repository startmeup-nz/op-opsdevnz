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
   - Add a new entry to `CHANGELOG.md` for every tagged version, even doc-only
     releases, so there is always an auditable note.

3. **Tests**
   ```
   make check
   ```

4. **Build the Distribution**
   ```
   rm -rf dist/
   python -m build
   python -m twine check dist/*
   ```

5. **Publish to TestPyPI**
   ```
   python -m twine upload --repository testpypi dist/*
   ```
   - Try installing it with
     ```
     pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple op-opsdevnz==<new-version>
     ```

6. **Tag + Push**
   ```
   git tag v<new-version>
   git push origin main v<new-version>
   ```

7. **PyPI (optional for now)**

   - Repeat step 5 with `--repository pypi` once TestPyPI validation passes.

## CI/CD

GitHub Actions runs lint, type-checking, tests, and a build on every push and
pull request, so releases should only require the manual TestPyPI upload plus a
tag.
