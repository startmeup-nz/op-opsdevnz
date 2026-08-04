# Functional Requirements

**Module:** op-opsdevnz<br />
**Status:** Draft

---

## Overview

op-opsdevnz resolves 1Password `op://` secret references in both CI environments (via service account tokens) and developer workstations (via the `op` CLI).

## Requirements

### FR-1: Resolve op:// references via Service Account SDK

The module SHALL resolve `op://Vault/Item/Field` references using the official 1Password Service Account SDK when `OP_SERVICE_ACCOUNT_TOKEN` is set.

### FR-2: Fallback to op CLI

When the SDK path is not configured (SDK not installed, or no service-account
token), the module SHALL fall back to the `op` CLI binary if installed and
authenticated. When the SDK path is configured and fails, the module SHALL
raise an error without falling back.

### FR-3: Environment override

The module SHALL support an environment variable override (e.g., `METANAME_API_TOKEN`) that takes precedence over 1Password resolution, for local development and testing.

### FR-4: Report resolver source

The module SHALL report which resolver produced the secret value (`sdk`, `cli`, or `env`).

### FR-5: CLI interface

The module SHALL provide a CLI (`op-opsdevnz resolve`) that follows the same
resolution semantics as the Python API. Output SHALL be an opaque mask by
default; the resolved value is printed only with the explicit `--no-mask`
flag.

### FR-6: OctoDNS integration

The module SHALL provide an OctoDNS hook (`op_opsdevnz.octodns_hooks:resolve`) for the Metaname provider.

---

## Related

- [Non-Functional Requirements](NFR.md)
- [Design Decisions](../design/README.md)
- [User Stories](../stories/README.md)
