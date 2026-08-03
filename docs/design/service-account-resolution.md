# Service-Account Resolution via the onepassword-sdk Client API

**Status:** Draft<br />
**Created:** 2026-08-03<br />
**Author:** OpsDev.nz Platform Engineering

---

## Problem

`src/opsdevnz/onepassword.py` resolves secrets through a Service Account SDK
interface that the installed SDK does not provide. The import sits in the
try/except at the top of the module; the calls run inside `_resolve_via_sdk()`:

```python
try:
    from onepassword import OnePassword
except Exception:  # pragma: no cover
    OnePassword = None

# inside _resolve_via_sdk():
op = OnePassword.from_environment()
value = op.secrets.resolve(secret_ref)
```

Since onepassword-sdk 0.4.0, the SDK exposes the async
`onepassword.client.Client` API and has no `OnePassword` class. The official
Service Account flow is documented in the
[SDK README](https://github.com/1Password/onepassword-sdk-python/blob/main/README.md#option-2-1password-service-account).
The import failure is caught by the `except Exception` above, so the module
imports cleanly while the SDK path stays permanently disabled.

The `OnePassword` interface is generated code: it was written against an
assumed API surface rather than the SDK's documented one, and it has never
matched any released version of `onepassword-sdk`. Because the CLI fallback
absorbed every failure (see [ADR-003](fallback-policy.md)), the mismatch went
unnoticed in normal use; it surfaced only when the resolution paths were
reviewed for this design work.

## Current Behaviour

- `_resolve_via_sdk()` always raises `SecretError("onepassword-sdk not
  installed")`, even when the SDK is present.
- `resolve_secret()` consequently falls back to the `op` CLI, or fails outright
  in service-account-only environments that have no `op` binary.
- The test suite passes because `test_sdk_used_when_available` installs a fake
  `OnePassword` object with `raising=False`, validating an interface that the
  SDK does not provide.
- A correct `Client`-based implementation already exists in
  `src/opsdevnz/onepassword_sdk.py`, but the primary resolver does not use it.

This breaks FR-1 (resolve `op://` references via the Service Account SDK) and
the advertised CI service-account story.

## Options Considered

1. **Move the Client flow into the primary resolver.** Port the implementation
   from `onepassword_sdk.py` into `onepassword.py`, wrapping the async SDK flow
   with `asyncio.run()` so `resolve_secret()` and `get_secret()` stay
   synchronous with unchanged signatures. `onepassword_sdk.py` remains as the
   async API for event-loop callers.

2. **Delegate from the primary resolver to `onepassword_sdk.py`.**
   `resolve_secret()` calls `get_secret_from_ref_env()` under the hood. Keeps
   two SDK modules with overlapping responsibilities, and the
   reference-environment-variable contract does not map cleanly onto
   `secret_ref`.

3. **Adopt a fully async public API.** Cleanest fit for the SDK, but breaks the
   synchronous `resolve_secret()` and `get_secret()` contract relied on by
   `octodns_hooks.py` and `oc-opsdevnz` `secrets.py`.

## Proposed Decision

Adopt option 1. One synchronous resolver, with the SDK flow sourced from the
verified `Client` API in `onepassword_sdk.py`:

- Authenticate per resolution for now, matching current `onepassword_sdk.py`
  behaviour. A cached client is a later optimisation, not part of this change.
- Preserve the integration metadata helpers (`_integration_meta()`,
  `_package_version()`) so SDK traffic identifies as "OpsDev.nz".
- Keep `SecretResolution.source` reporting so callers can verify the principal.

## Guardrails (with issue #8)

- Tests must import the real SDK symbols and fail when the adapter references a
  missing symbol. The `raising=False` fake must be removed. Mypy cannot catch
  this class of error because `ignore_missing_imports` is enabled, so the
  test-level import guard is the enforcement point.
- The import guard must narrow to `except ImportError`, or be removed once the
  real `Client` import lands. A bare `except Exception` silently reclassifies
  genuine runtime bugs in the new code path as "SDK not installed", the same
  way the current guard hides the interface mismatch.
- CI must build the wheel, install it, import the package, and smoke-test the
  CLI before release, so the packaged artifact is verified.
- `RELEASING.md` describes a TestPyPI smoke-test stage that `publish.yml` does
  not implement; align the workflow with the documented stage.

## Consequences

- The sync resolver is a hard API contract: `resolve_secret()` must not be
  invoked from within a running event loop, because the `asyncio.run()` bridge
  fails there. Async callers must use the async API in `onepassword_sdk.py`
  directly. OctoDNS provider chains can run in async contexts depending on how
  the provider chain is invoked, so the constraint binds current and future
  callers.

## Open Questions

- Whether to cache the authenticated `Client` across resolutions within one
  process. Avoids per-call authentication; complicates token rotation.

## More Information

- Issue [#9](https://github.com/startmeup-nz/op-opsdevnz/issues/9): Fix
  service-account resolution to use the real onepassword-sdk Client API.
- Issue [#8](https://github.com/startmeup-nz/op-opsdevnz/issues/8): Repair SDK
  integration and consolidate the public package namespace.
