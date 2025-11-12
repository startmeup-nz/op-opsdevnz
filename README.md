# op-opsdevnz

[![CI](https://github.com/startmeup-nz/op-opsdevnz/actions/workflows/ci.yml/badge.svg)](https://github.com/startmeup-nz/op-opsdevnz/actions/workflows/ci.yml)

Python package for resolving 1Password `op://` secrets across CI service accounts and developer workstations, plus a CLI fallback that depends on the authenticated 1Password CLI binary. Keeps OctoDNS and other automation workflows secret-free. Packaged for reuse by OpsDev.nz, a platform engineering collective sponsored by StartMeUp.nz.

## Features

- Resolve `op://` references via the official Service Account SDK with optional
  CLI fallback for local workflows.
- Rich error handling plus an API that can return the secret value *and* which
  resolver was used.
- Environment override helpers for CI sandboxes/tests.
- OctoDNS hook (`opsdevnz.octodns_hooks.resolve`) for the Metaname provider.
- Small CLI (`op-opsdevnz resolve …`) that mirrors the `resolve_secret()`
  helper so shell scripts match the Python API semantics.

## Installation

```bash
# editable install while developing locally
pip install -e modules/op_opsdevnz

# latest release from PyPI
pip install op-opsdevnz

# or install straight from GitHub if you need main branch changes
pip install git+https://github.com/startmeup-nz/op-opsdevnz.git
```

## Usage

```python
from opsdevnz.onepassword import resolve_secret

result = resolve_secret(
    secret_ref_env="METANAME_API_TOKEN_REF",
    env_override="METANAME_API_TOKEN",
)
print(result.value, result.source)  # -> ('***', 'sdk' | 'cli' | 'env')
```

CLI equivalent:

```bash
op-opsdevnz resolve --ref "op://Vault/Item/Field" --show-source
op-opsdevnz resolve --ref-env METANAME_API_TOKEN_REF --env-override METANAME_API_TOKEN
```

### OctoDNS Hook

Set the resolver environment variable so the OctoDNS Metaname provider can load
the helper automatically:

```bash
export OCTODNS_METANAME_SECRET_RESOLVER="op_opsdevnz.octodns_hooks:resolve"
```

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
