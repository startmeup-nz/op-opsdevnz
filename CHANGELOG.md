# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-08-04

Implements the design decisions from PR #10 (ADRs 001–003) and resolves
issues #8 and #9.

### Breaking

- **Namespace consolidation (ADR-002):** the implementation moved to
  `op_opsdevnz`, matching the distribution name and every documented
  consumer. The legacy `opsdevnz` package and its wildcard shim were removed.
  Update imports from `opsdevnz.*` to `op_opsdevnz.*`. The console script
  entry point is now `op_opsdevnz.__main__:main` (the `op-opsdevnz` command
  itself is unchanged).
- **Fallback policy (ADR-003):** the resolver no longer falls back from a
  configured-but-failing SDK to the local `op` CLI. `SdkAuthError` is raised
  instead, so credential principals never switch silently. Fallback is
  allowed only when the SDK path is not configured (`SdkNotConfiguredError`).
  Both new errors subclass `SecretError`.

### Fixed

- **Service-account resolution (ADR-001, #9):** the SDK path now uses the
  real `onepassword-sdk` `Client.authenticate()` / `client.secrets.resolve()`
  async API, replacing a nonexistent `onepassword.OnePassword` interface that
  never shipped in any released SDK. Sync entry points are unchanged and now
  fail with a clear error when called from a running event loop; async
  callers use `op_opsdevnz.onepassword_sdk.resolve_secret_async()`.
- Integration version sent to the SDK no longer contains build metadata
  (`+`), which the SDK rejects.
- The OctoDNS hook no longer forces CLI-first resolution when a
  service-account token is configured.

### Security

- Error messages and stack traces no longer include secret values, fragments,
  full `op://` references, raw `op` CLI stderr, or raw SDK diagnostics.
- CLI output is a fixed opaque mask (`********`) by default; it no longer
  reveals the first/last characters or the length of a secret. `--no-mask`
  prints the resolved value explicitly.
- Bandit now fails the build on medium severity and above (was non-enforcing
  `|| true`), and pip-audit audits the project's installed dependency set.
  Policy documented in SECURITY.md.

### Added

- Test suite covers the SDK adapter, fallback classification, sanitization,
  CLI, OctoDNS hook, env loader, timeout, and failure branches, with an
  enforced 90% coverage threshold. A contract test imports the real SDK
  symbols so a renamed/removed SDK API fails the suite (the `raising=False`
  fake is gone).
- CI consolidates `ci.yml`/`test.yml`, and adds a build job that verifies
  wheel contents, installs the wheel into a clean venv, and smoke-tests
  canonical imports and the CLI.
- Release pipeline (`publish.yml`) gates on tag/version agreement and the
  full test suite, and implements the documented TestPyPI smoke-test stage
  before publishing to PyPI.
- `.env.refs.*` files are un-ignored in `.gitignore`, matching the documented
  "safe to commit" guidance.

## [0.1.5] - 2026-08-04
### Changed
- Added design ADRs for SDK resolution, public namespace, and fallback policy
  (PR #10), and aligned NFR-3/FR-2 (conditional fallback) and NFR-5 (Python
  3.12+) with the agreed design.

## [0.1.4] - 2025-11-12
### Added
- First production PyPI release, enabling downstream repos to depend on
  `op-opsdevnz` without editable installs.

### Changed
- Installation docs now highlight the PyPI workflow plus the GitHub fallback.
- Releasing guide documents the TestPyPI → PyPI upload sequence.
- Internal consumers swept so requirements/docs reference the published wheel.

## [0.1.3] - 2025-11-12
### Changed
- README feature list now explicitly references `resolve_secret()` so the
  CLI equivalence statement is unambiguous.

## [0.1.2] - 2025-11-12
### Changed
- README intro now clarifies the package scope, CLI requirements, and broader
  automation audiences.
- RELEASING checklist updated with mandatory changelog entries, `twine check`,
  and pinned TestPyPI install steps for doc-only releases.

## [0.1.1-2] - 2025-11-12
### Added
- Introduced `resolve_secret()` to return both the secret value and the resolver
  source (`env`, `sdk`, or `cli`). `get_secret()` now wraps this helper for
  backwards compatibility.
- CLI `op-opsdevnz resolve` gains `--show-source` to surface which resolver was
  used.
- Added packaging scaffolding (LICENSE, README refresh, CONTRIBUTING,
  SECURITY, RELEASING, Makefile, GitHub Actions CI) and tightened metadata for
  TestPyPI publication.

### Changed
- Migration from OpsDev.nz monorepo to self contained GitHub repo.
- Repository reorganized so the canonical modules live under `opsdevnz.*` with
  compatibility wrappers exposed via `op_opsdevnz.*`.

## [0.1.0] - 2025-10-31
- Initial module release in the OpsDev.nz GitLab monorepo.
- Based on op-smunz an initial unpublished 1password helper module.
