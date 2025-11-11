# op-opsdevnz

Helpers to resolve 1Password secrets in both local development and CI.

## Features

- Resolve `op://` references using the 1Password Service Account SDK with CLI
  fallback (for local interactive sessions).
- Optional environment overrides so developers can inject test values without
  rewriting config.
- OctoDNS integration helper (`opsdevnz.octodns_hooks.resolve`) for use with the
  Metaname provider.
- Small CLI (`op-opsdevnz resolve …`) that mirrors the Python helper behaviour.

## Installation

```bash
pip install -e modules/op_opsdevnz
```

## Usage

```python
from opsdevnz.onepassword import get_secret

token = get_secret(secret_ref_env="METANAME_API_TOKEN_REF", env_override="METANAME_API_TOKEN")
```

CLI equivalent:

```bash
op-opsdevnz resolve --ref "op://Vault/Item/Field"
op-opsdevnz resolve --ref-env METANAME_API_TOKEN_REF --show-source
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
ruff check src tests
pytest
```

## License

Apache-2.0 © OpsDev.nz
