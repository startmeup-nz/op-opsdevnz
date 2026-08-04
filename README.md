# op-opsdevnz

[![CI](https://github.com/startmeup-nz/op-opsdevnz/actions/workflows/ci.yml/badge.svg)](https://github.com/startmeup-nz/op-opsdevnz/actions/workflows/ci.yml)

Python package for resolving 1Password `op://` secrets across CI service accounts and developer workstations, plus a CLI fallback that depends on the authenticated 1Password CLI binary. Keeps OctoDNS and other automation workflows secret-free. Packaged for reuse by OpsDev.nz, a platform engineering collective sponsored by StartMeUp.nz.

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
- OctoDNS hook (`op_opsdevnz.octodns_hooks.resolve`) for the Metaname provider.
- Small CLI (`op-opsdevnz resolve …`) that follows the same resolution
  semantics as `resolve_secret()`. Output is an opaque mask by default;
  `--no-mask` prints the resolved value.

## Installation

```bash
# editable install while developing locally
pip install -e .

# latest release from PyPI
pip install op-opsdevnz

# or install straight from GitHub if you need main branch changes
pip install git+https://github.com/startmeup-nz/op-opsdevnz.git
```

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

### OctoDNS Hook

Set the resolver environment variable so the OctoDNS Metaname provider can load
the helper automatically:

```bash
export OCTODNS_METANAME_SECRET_RESOLVER="op_opsdevnz.octodns_hooks:resolve"
```

The hook resolves CLI-first on workstations (no token) and SDK-first when
`OP_SERVICE_ACCOUNT_TOKEN` is set, matching the fallback policy above.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
make check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and
[RELEASING.md](RELEASING.md) for publishing instructions.

## License

Apache-2.0 © OpsDev.nz
