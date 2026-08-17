# Service-Account Resolution via the onepassword-sdk Client API

**Status:** Accepted and implemented (0.2.0+)<br />
**Created:** 2026-08-03<br />
**Author:** OpsDev.nz Platform Engineering

---

## Summary

The SDK path now uses the real `onepassword-sdk` `Client.authenticate()` /
`client.secrets.resolve()` async API, wrapped with `asyncio.run()` for
synchronous callers. The resolver authenticates per resolution and identifies
as "OpsDev.nz" via integration metadata.

## Problem (historical)

The original implementation used a `OnePassword` class that didn't exist in
the SDK:

```python
try:
    from onepassword import OnePassword
except Exception:
    OnePassword = None

# inside _resolve_via_sdk():
op = OnePassword.from_environment()
value = op.secrets.resolve(secret_ref)
```

This interface was generated code written against an assumed API surface. It
never matched any released version of `onepassword-sdk`. The `except Exception`
guard silently swallowed the import failure, so the module loaded cleanly while
the SDK path stayed permanently disabled. The CLI fallback absorbed every
failure, so the mismatch went unnoticed until the resolution paths were reviewed.

## Implemented Behaviour

### SDK resolution flow

```
_resolve_via_sdk(secret_ref)
├── Check: Client imported? → No → raise SdkNotConfiguredError
├── Check: OP_SERVICE_ACCOUNT_TOKEN set? → No → raise SdkNotConfiguredError
├── Client.authenticate(auth=token) → async
├── client.secrets.resolve(secret_ref) → async
└── Return value
```

### Sync/async split

- **`resolve_secret()`** — synchronous, uses `asyncio.run()` to bridge the
  async SDK. Must not be called from within a running event loop.
- **`_resolve_ref_async()`** — async, for event-loop callers.
- Both share the same authentication and resolution logic.

### Integration metadata

Every SDK call includes metadata identifying the caller:

```python
{
    "integration_name": "OpsDev.nz",
    "integration_version": "0.3.0",  # from package metadata
}
```

The version is stripped of build metadata (`+`) because the SDK rejects it.

## Guardrails

- Tests import real SDK symbols and fail when the adapter references a missing
  symbol. The `raising=False` fake was removed.
- The import guard uses `except ImportError` (not bare `except Exception`) to
  avoid silently reclassifying runtime bugs as "SDK not installed".
- `_package_version()` returns a plain semver fallback (`"0.0.0"`) when package
  metadata is unavailable, avoiding the SDK's build-metadata rejection.

## API contracts

- `resolve_secret()` must not be invoked from within a running event loop —
  the `asyncio.run()` bridge fails there. Async callers use
  `_resolve_ref_async()` directly.
- `SecretResolution.source` reports which resolver produced the value (`"env"`,
  `"sdk"`, or `"cli"`), so callers can verify the principal.

## More Information

- Issue [#9](https://github.com/startmeup-nz/op-opsdevnz/issues/9): Fix
  service-account resolution to use the real onepassword-sdk Client API.
- Issue [#8](https://github.com/startmeup-nz/op-opsdevnz/issues/8): Repair SDK
  integration and consolidate the public package namespace.
