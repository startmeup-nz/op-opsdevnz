# Public Namespace Consolidation

**Status:** Draft
**Created:** 2026-08-03
**Author:** OpsDev.nz Platform Engineering

---

## Problem

The `op-opsdevnz` distribution ships two top-level packages:

- `src/opsdevnz/`, the implementation, including the console script entry
  point `opsdevnz.__main__:main`.
- `src/op_opsdevnz/`, a compatibility shim that re-exports the implementation
  with wildcard imports.

Consumers cannot tell which import path is stable, and the docs disagree:

| Surface | Namespace |
|---------|-----------|
| Distribution name | `op-opsdevnz` |
| Console script | `opsdevnz.__main__:main` |
| README and index examples | `from opsdevnz.onepassword import ...` |
| FR-6 and AGENTS.md resolver string | `op_opsdevnz.octodns_hooks:resolve` |
| oc-opsdevnz imports | `from op_opsdevnz.onepassword import ...` |

## Evidence

Sibling modules follow the convention package = distribution name with dashes
replaced by underscores:

- `oc-opsdevnz` ships `oc_opsdevnz`.
- `worklog-opsdevnz` ships `worklog_opsdevnz`.

External consumers already import `op_opsdevnz`:

- `oc-opsdevnz` in `src/oc_opsdevnz/secrets.py` and four example scripts.
- `octodns-metaname` via `OCTODNS_METANAME_SECRET_RESOLVER`.

## Options Considered

1. **Canonicalize `op_opsdevnz`.** Move the implementation from `src/opsdevnz/`
   to `src/op_opsdevnz/`, delete the shim, update the console script entry to
   `op_opsdevnz.__main__:main`, and update README, index, and test
   monkeypatch targets. Matches the distro name, sibling convention, and every
   external consumer.

2. **Canonicalize `opsdevnz`.** Rename the distribution to `opsdevnz`, update
   `oc-opsdevnz` and `octodns-metaname` references, and change the documented
   resolver string. Breaks the sibling naming pattern and existing consumers.

3. **Keep both and document a canonical choice.** Preserves the ambiguity and
   the duplicated surface; both packages must be maintained and shipped.

## Proposed Decision

Adopt option 1. Single package `op_opsdevnz`. Release as 0.2.0, since the
import path for `opsdevnz` users is a breaking change; acceptable at 0.x per
the versioning policy in AGENTS.md.

Notes:

- Keeping `opsdevnz` as a generic top-level name also risks colliding with a
  future shared utilities namespace. Module-scoped naming avoids squatting a
  generic name.
- Coordinate the change with `octodns-metaname` and `oc-opsdevnz` docs that
  reference the module.

## Open Questions

- Whether to ship one deprecation release that keeps `opsdevnz` as a shim
  pointing at `op_opsdevnz`, or to remove the shim in the same release.

## More Information

- Issue [#8](https://github.com/startmeup-nz/op-opsdevnz/issues/8): Repair SDK
  integration and consolidate the public package namespace.
