# AGENTS.md — op-opsdevnz

**Audience:** Contributors and AI assistants working on the op-opsdevnz module.

## IMPORTANT: No Autonomous Commits

AI assistants must NOT commit changes to this repository. Always stage changes
and describe what was done, then wait for human review and confirmation before
committing. This ensures all changes have human oversight.

## Module Scope

op-opsdevnz provides 1Password secret resolution for OpsDev.nz automation. It
wraps the official 1Password Service Account SDK with an optional fallback to
the `op` CLI for local development workflows. The module keeps automation code
secret-free by resolving `op://` references at runtime.

## Zensical Documentation Server

**AI assistants should NOT start the Zensical dev server.** The human developer
controls when and where `zensical serve` runs — it binds a port and stays
running, which is a human-level decision.

AI assistants MAY:

- Run `uv run zensical build` to verify docs render without errors
- Edit `zensical.toml` configuration
- Edit markdown files under `docs/`

## Development Workflow

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run python -m pytest tests/ -v

# Lint
uv run ruff check src tests

# Build docs (verify render, no errors)
uv run zensical build
```

## Testing

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run a specific test file
uv run python -m pytest tests/test_onepassword.py -v
```

## Secret Resolution

Users resolve 1Password secrets via `op_opsdevnz`:

```bash
export OCTODNS_METANAME_SECRET_RESOLVER="op_opsdevnz.octodns_hooks:resolve"
```

CI environments rely on `_REF` variables pointing to 1Password references.

## Versioning

- **0.0.x** — Incubation phase, rapid iteration, breaking changes expected
- **0.1.0** — First public release, API stabilises
- **1.0.0** — Stable release, semantic versioning enforced

## Finding Current Work

This is a GitHub repository. To understand what work is in progress or planned:

1. **Check open issues:** `gh issue list` or visit the Issues tab
2. **Check open PRs:** `gh pr list` or visit the Pull Requests tab
3. **Review documentation:** Read `docs/` for specifications, design decisions, and user stories
4. **Check milestones:** `gh api repos/{owner}/{repo}/milestones` for planned releases

Work items are tracked via GitHub issues and pull requests, not in this file.

## Git Signing

This repository is frequently edited by AI agents.

- Never disable or bypass the default git signing configuration.
- Run commits/pushes normally so the signing prompt can appear for the operator.

## Related

- [OpsDev.nz Collective](https://opsdev.nz) — Parent project
- [Module template](https://github.com/startmeup-nz/practice-template-opsdevnz)
