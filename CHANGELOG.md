# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2025-11-12
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
