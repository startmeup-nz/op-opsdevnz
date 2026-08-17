# SDK-to-CLI Fallback Policy

**Status:** Accepted and implemented (0.2.0+)<br />
**Created:** 2026-08-03<br />
**Author:** OpsDev.nz Platform Engineering

---

## Summary

When the SDK path is configured (`OP_SERVICE_ACCOUNT_TOKEN` is set), any SDK
failure is a **hard failure** — no fallback to the CLI. This prevents silent
principal switching. Fallback is only allowed when the SDK path is not
configured (token absent, SDK not installed).

## Problem (historical)

Previously, `resolve_secret()` fell back from the Service Account SDK to the
`op` CLI on any `SecretError`, and the OctoDNS hook forced `prefer_cli=True`,
which inverts the order to CLI-first.

A process configured with a narrowly scoped service-account token could silently
resolve through a developer's broader, locally authenticated `op` CLI session.
Authentication and authorization failures should not switch principals without
the caller knowing.

## Implemented Behaviour

The resolver distinguishes between two error states:

- **`SdkNotConfiguredError`** — fallback to CLI allowed: token absent, or the
  SDK import fails.
- **`SdkAuthError`** — hard failure, no fallback: any error from
  `Client.authenticate()` or `client.secrets.resolve()` while the SDK path
  is configured.

The rule is binary: once the SDK path is configured, any failure — including
transient ones such as rate limits — is a hard failure. No principal switching.

### Resolution flow (default, `prefer_cli=False`)

```
SDK configured (OP_SERVICE_ACCOUNT_TOKEN set)?
├── Yes → Try SDK
│   ├── Success → done (source="sdk")
│   └── Failure (SdkAuthError) → HARD FAIL, no CLI fallback
└── No (SdkNotConfiguredError) → CLI fallback allowed if `op` available
```

### Resolution flow (CLI-first, `prefer_cli=True`)

Used by provider adapters (e.g., `octodns_metaname.op_opsdevnz_hooks:resolve`)
on workstations where the signed-in `op` session is the intended principal:

```
Try CLI first
├── Success → done (source="cli")
└── Failure → Try SDK
    ├── Success → done (source="sdk")
    └── Failure → re-raise CLI error
```

### CI behaviour

With `OP_SERVICE_ACCOUNT_TOKEN` set, the CLI authenticates as the same
service-account principal the SDK would use. Both paths are interchangeable
in CI — the identity-switch risk from issue #8 is a workstation concern, where
a human `op` session can sit next to a service-account token.

## Why two error classes?

The SDK exposes no typed exceptions for "not configured" versus "auth failed":
a rejected token raises a bare `Exception("invalid user input: ...")`, and the
only typed exceptions are `DesktopSessionExpiredException` (desktop-app only)
and `RateLimitExceededException`. So the resolver's pre-checks decide:

- Token absent? → `SdkNotConfiguredError`
- SDK import fails? → `SdkNotConfiguredError`
- Any error from `Client.authenticate()` or `client.secrets.resolve()`? →
  `SdkAuthError`

## Implementation Order (historical)

ADR-001 (SDK integration) landed before ADR-003 (this policy). Until the SDK
path worked, `_resolve_via_sdk()` always raised `SecretError("onepassword-sdk
not installed")` — which would have been misclassified as `SdkAuthError` (hard
failure) if ADR-003 shipped first. Sequencing ADR-001 first avoided the
transitional rule entirely.

## Resolved Questions

- **Pinning a required source.** Deferred. Callers can already assert
  `resolution.source == "sdk"` after the fact, and this ADR's binary rule
  removes the dangerous silent fallback.
- **Which SDK exceptions map to "not configured" versus "auth failed".**
  None do: the SDK raises a bare `Exception` for token rejection. Classification
  is by configuration state, decided by the resolver's pre-checks.

## More Information

- Issue [#8](https://github.com/startmeup-nz/op-opsdevnz/issues/8): Repair SDK
  integration and consolidate the public package namespace.
- Issue [#9](https://github.com/startmeup-nz/op-opsdevnz/issues/9): Fix
  service-account resolution to use the real onepassword-sdk Client API.
