# op-opsdevnz

[![CI](https://github.com/startmeup-nz/op-opsdevnz/actions/workflows/ci.yml/badge.svg)](https://github.com/startmeup-nz/op-opsdevnz/actions/workflows/ci.yml)

Resolve 1Password `op://` secret references at runtime so automation code
stays secret-free. Resolution uses the official 1Password Service Account SDK
for CI, with a conditional fallback to the `op` CLI for local development —
and a strict security posture: credential principals never switch silently,
and errors never leak secret values, fragments, or references.

Maintained by OpsDev.nz, a platform engineering collective sponsored by
StartMeUp.nz.

## Features

- Resolve `op://` references via the official Service Account SDK with a
  conditional CLI fallback for local workflows.
- Explicit fallback policy: the CLI is used only when the SDK path is not
  configured. A configured-but-failing SDK is a hard error, so resolution
  never silently switches credential principals.
- Sanitized errors: failure output never includes secret values, fragments,
  `op://` references, or raw subprocess/SDK diagnostics.
- Rich error handling plus an API that can return the secret value *and* which
  resolver was used.
- Environment override helpers for CI sandboxes/tests.
- Small CLI (`op-opsdevnz resolve …`) that follows the same resolution
  semantics as `resolve_secret()`. Output is an opaque mask by default;
  `--no-mask` prints the resolved value.

## Installation

```bash
# latest release from PyPI
pip install op-opsdevnz

# or install straight from GitHub if you need main branch changes
pip install git+https://github.com/startmeup-nz/op-opsdevnz.git
```

Requires Python 3.12+ and one of:

- **CI / automation:** `OP_SERVICE_ACCOUNT_TOKEN` set (a
  [1Password Service Account](https://developer.1password.com/docs/service-accounts/))
- **Workstations:** the [1Password CLI](https://developer.1password.com/docs/cli/)
  installed and signed in (`op signin`)

## Usage

```python
from op_opsdevnz.onepassword import resolve_secret

result = resolve_secret(
    secret_ref_env="METANAME_API_TOKEN_REF",
    env_override="METANAME_API_TOKEN",
)
print(result.value, result.source)  # -> ('***', 'sdk' | 'cli' | 'env')
```

The canonical import package is `op_opsdevnz` (matching the `op-opsdevnz`
distribution name). The legacy `opsdevnz` package was removed in 0.2.0.

CLI equivalent:

```bash
op-opsdevnz resolve --ref "op://Vault/Item/Field" --show-source
op-opsdevnz resolve --ref-env METANAME_API_TOKEN_REF --env-override METANAME_API_TOKEN
op-opsdevnz resolve --ref "op://Vault/Item/Field" --no-mask  # print the value
```

### Async Usage

`resolve_secret()` and `get_secret()` are synchronous and must not be called
from within a running event loop (they bridge the SDK with `asyncio.run()`
and raise a clear error there). Async callers use the async API directly:

```python
from op_opsdevnz.onepassword_sdk import resolve_secret_async

value = await resolve_secret_async("op://Vault/Item/Field")
```

### Secret Reference Files

For per-environment reference files (references only — no secret values, safe
to commit):

```python
from op_opsdevnz.env import load_refs

load_refs("staging")  # loads .env.staging into the environment
```

### Fallback Policy

Resolution follows a strict rule (see `docs/design/fallback-policy.md`):

- **Default (SDK first):** with `OP_SERVICE_ACCOUNT_TOKEN` set, the Service
  Account SDK resolves the reference. Any SDK failure — authentication,
  authorization, resolution, rate limit — raises `SdkAuthError` and the CLI
  is **not** tried.
- **Not configured:** without a token (or without the SDK installed),
  `SdkNotConfiguredError` is raised internally and resolution falls back to
  the locally authenticated `op` CLI.
- **`prefer_cli=True`:** workstations can opt into CLI-first resolution; the
  SDK remains the fallback so CI/service-account flows keep working.

Error classes `SdkNotConfiguredError` and `SdkAuthError` subclass
`SecretError`, so existing `except SecretError` handlers keep working.

### OctoDNS integration

The Metaname-specific resolver adapter lives in the `octodns-metaname` module,
which uses this package for generic 1Password resolution.

## Development

```bash
uv sync --extra dev
uv run ruff check src tests
uv run mypy src
uv run python -m pytest tests/ --cov
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and
[RELEASING.md](RELEASING.md) for publishing instructions.

## License

Apache-2.0 © OpsDev.nz
