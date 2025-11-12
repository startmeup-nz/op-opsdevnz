# Changelog

All notable changes to this project will be documented in this file.

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
