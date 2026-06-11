# op-opsdevnz

Python package for resolving 1Password `op://` secrets across CI service accounts and developer workstations.

- **Status:** Development
- **License:** Apache 2.0
- **Python:** 3.12+

## Overview

op-opsdevnz provides a thin wrapper around the official 1Password Service Account SDK with an optional fallback to the `op` CLI for local development workflows. It keeps automation code secret-free by resolving `op://` references at runtime.

The package supports both CI environments (via service account tokens) and developer workstations (via the 1Password CLI), with a consistent API that reports which resolver was used.

## Quick Start

```bash
# Install
uv pip install op-opsdevnz

# Resolve a secret
op-opsdevnz resolve --ref "op://Vault/Item/Field" --show-source

# Or use the Python API
from opsdevnz.onepassword import resolve_secret

result = resolve_secret(
    secret_ref_env="METANAME_API_TOKEN_REF",
    env_override="METANAME_API_TOKEN",
)
print(result.value, result.source)  # -> ('***', 'sdk' | 'cli' | 'env')
```

## Documentation

- **[Specifications](specs/)** — Functional and non-functional requirements
- **[Design Decisions](design/README.md)** — Architecture choices and rationale
- **[User Stories](stories/README.md)** — Persona-driven narratives

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run python -m pytest tests/ -v

# Lint
uv run ruff check src tests

# Build docs (verify render)
uv run zensical build
```

## Related

- [OpsDev.nz Collective](https://opsdev.nz) — Parent project
- [Module template](https://github.com/startmeup-nz/practice-template-opsdevnz)
