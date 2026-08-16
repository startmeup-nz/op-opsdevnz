# Public Namespace Consolidation

**Status:** Accepted (implemented in 0.2.0)<br />
**Created:** 2026-08-03<br />
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
| Metaname resolver adapter | `octodns_metaname.op_opsdevnz_hooks:resolve` |
| oc-opsdevnz imports | `from op_opsdevnz.onepassword import ...` |

## Evidence

Sibling modules follow the convention package = distribution name with dashes
replaced by underscores:

- `oc-opsdevnz` ships `oc_opsdevnz`.
- `worklog-opsdevnz` ships `worklog_opsdevnz`.

External consumers already import `op_opsdevnz`:

- `oc-opsdevnz` in `src/oc_opsdevnz/secrets.py` and four example scripts.
- `octodns-metaname` via its provider-owned `OCTODNS_METANAME_SECRET_RESOLVER` adapter.

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
- No deprecation shim: remove `opsdevnz` in the same 0.2.0 release and note the
  import path change in the changelog. External consumers already import
  `op_opsdevnz`, and the 0.x versioning policy permits the breaking change.
- If the package gains a `py.typed` marker or type stubs before the move, they
  must move with the package; one left behind in `src/opsdevnz/` would claim
  typing support for a package that no longer exists.

## More Information

- Issue [#8](https://github.com/startmeup-nz/op-opsdevnz/issues/8): Repair SDK
  integration and consolidate the public package namespace.
