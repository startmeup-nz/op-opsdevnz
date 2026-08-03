# SDK-to-CLI Fallback Policy

**Status:** Draft<br />
**Created:** 2026-08-03<br />
**Author:** OpsDev.nz Platform Engineering

---

## Problem

`resolve_secret()` falls back from the Service Account SDK to the `op` CLI on
any `SecretError`, and `octodns_hooks.py` forces `prefer_cli=True`, which
inverts the order to CLI-first.

A process configured with a narrowly scoped service-account token can silently
resolve through a developer's broader, locally authenticated `op` CLI session.
Authentication and authorization failures should not switch principals without
the caller knowing.

NFR-3 currently mandates unconditional fallback. It is reworded to conditional
fallback with this change, so the requirement describes the same policy as this
ADR (see Resolved Questions).

## Current Behaviour

- SDK failure of any kind, including token rejection, falls through to the CLI.
- `octodns_hooks.py` always resolves via the CLI first when `op` is present,
  regardless of whether a service-account token is configured.
- In CI, the `op` CLI is installed in the `python-opcli` container image and
  authenticates via `OP_SERVICE_ACCOUNT_TOKEN`, so CLI resolution runs as the
  same service-account principal the SDK would use. Pipelines pass for this
  reason; the SDK path itself has never worked (see
  [ADR-001](service-account-resolution.md)).
- The unconditional fallback is why the SDK mismatch in ADR-001 went unnoticed:
  every failure was absorbed by the CLI, so the dead interface never surfaced
  until the resolution paths were reviewed.

## Options Considered

1. **Strict, no automatic fallback.** Only explicit `prefer_cli=True` uses the
   CLI. Any failure of the configured principal is a hard error. Simplest
   security model, but removes the workstation convenience the module
   advertises (NFR-3 becomes explicit-choice only).

2. **Conditional fallback.** Fall back from SDK to CLI only when the SDK path
   is unavailable by configuration: SDK not installed,
   `OP_SERVICE_ACCOUNT_TOKEN` not set, or `op` absent. Hard-fail when the SDK
   is configured and present but authentication or authorization fails. Keeps
   the workstation workflow and prevents silent principal switching.

3. **Keep current behaviour and document the caveat.** No code change, but the
   risk remains for any automation that runs on a machine with both a token
   and a signed-in CLI.

## Proposed Decision

Adopt option 2. Introduce a distinction between configuration absence and
runtime auth failure:

- Two `SecretError` subclasses: `SdkNotConfiguredError` and `SdkAuthError`.
  The resolver decides which to raise from its own pre-checks and call
  context, never by inspecting SDK exception types.
- Classification is by configuration state, not exception type. The SDK
  exposes no typed exceptions for "not configured" versus "auth failed": a
  rejected token raises a bare `Exception("invalid user input: ...")`
  (verified empirically against onepassword-sdk 0.4.0), and the only typed
  exceptions in the SDK are `DesktopSessionExpiredException` (desktop-app
  only, not the service-account path) and `RateLimitExceededException`.
  So the resolver's pre-checks decide:
  - `SdkNotConfiguredError` — fallback to CLI allowed: token absent, or the
    SDK import fails.
  - `SdkAuthError` — hard failure, no fallback: any error from
    `Client.authenticate()` or `client.secrets.resolve()` while the SDK path
    is configured.
- The rule is binary: once the SDK path is configured, any failure — including
  transient ones such as rate limits — is a hard failure. No principal
  switching.
- Revisit `octodns_hooks.py`: `prefer_cli` should not be forced unconditionally.
  In CI, the CLI and the SDK resolve as the same principal, so the hook should
  let the SDK path run once it works ([ADR-001](service-account-resolution.md)).
  CLI-first stays the right default for workstations, where the signed-in `op`
  session is the intended principal.
- Keep `SecretResolution.source` so automation can log and assert which
  principal produced the value.

CI nuance: with `OP_SERVICE_ACCOUNT_TOKEN` set, the CLI authenticates as the
same service-account principal the SDK would use, so CLI-first resolution in
the pipeline is not a credential downgrade. The identity-switch risk from
issue \#8 is a workstation concern, where a human `op` session can sit next
to a service-account token. The conditional fallback above targets that
case; in CI the two paths are interchangeable.

## Implementation Order

ADR-001 must land before ADR-003. Until the SDK path works,
`_resolve_via_sdk()` raises `SecretError("onepassword-sdk not installed")`
even when the SDK is installed. If ADR-003 shipped first, that error would
need a transitional classification: map it to `SdkNotConfiguredError`
(fallback allowed), not `SdkAuthError` (hard failure), or every workstation's
silent-but-working CLI fallback would become a hard failure, because the
current failure mode would be bucketed as "configured but broken" rather than
"not configured". Sequencing ADR-001 first avoids the transitional rule
entirely.

## Resolved Questions (2026-08-04)

- **Pinning a required source.** Deferred. Callers can already assert
  `resolution.source == "sdk"` (FR-4) after the fact, and this ADR's binary
  rule removes the dangerous silent fallback. No consumer has asked for
  first-class pinning; revisit if one does.
- **Which SDK exceptions map to "not configured" versus "auth failed".**
  None do: the SDK raises a bare `Exception` for token rejection and has no
  typed "not configured" exception (see Proposed Decision). Classification is
  by configuration state, decided by the resolver's pre-checks.
- **Whether NFR-3 needs rewording.** Yes — and FR-2 too. Both are reworded to
  conditional fallback in this change, so the specs and this ADR describe the
  same policy.

## More Information

- Issue [#8](https://github.com/startmeup-nz/op-opsdevnz/issues/8): Repair SDK
  integration and consolidate the public package namespace.
- [NFRs](../specs/NFR.md), NFR-3 graceful fallback.
