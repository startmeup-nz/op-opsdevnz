# Security Policy

We take the safety of automation workloads seriously. If you discover a
vulnerability in `op-opsdevnz`, please email
[john@opsdev.nz](mailto:john@opsdev.nz). When possible, encrypt the report
using the GPG key published on [pgp.net.nz](https://pgp.net.nz/) for that
address. Public issues or pull requests should be avoided until we have a fix
ready.

When reporting:

1. Include a proof-of-concept or reproduction steps.
2. Share the impact (e.g., credential disclosure, privilege escalation).
3. Provide the versions/commit hashes you tested.

We aim to acknowledge new reports within 2 business days and will keep you
updated as we investigate.

## Security Guarantees

The resolver is a trust boundary between 1Password and automation. Since
0.2.0 it enforces:

- **No silent principal switching.** Once the Service Account SDK path is
  configured (`OP_SERVICE_ACCOUNT_TOKEN` set), any SDK failure is a hard
  error (`SdkAuthError`). Resolution only falls back to the local `op` CLI
  when the SDK path is not configured. See
  [`docs/design/fallback-policy.md`](docs/design/fallback-policy.md).
- **Sanitized errors.** Error messages and stack traces never include secret
  values, fragments, full `op://` references, raw `op` CLI stderr, or raw SDK
  diagnostics (NFR-1/NFR-2).
- **Opaque CLI output.** `op-opsdevnz resolve` prints a fixed `********`
  mask by default — no characters, no length leakage. `--no-mask` prints the
  resolved value explicitly.

## Pipeline Policy (SAST / dependency audit)

The `sast.yml` workflow enforces:

- **Bandit** fails the build on medium severity and above (`-ll`).
  Low-severity findings (e.g. the accepted `subprocess` usage with list
  arguments and no shell) are still uploaded to the GitHub Security tab as
  SARIF for visibility.
- **pip-audit** audits the project's own dependency set (the project is
  installed before auditing); known vulnerabilities fail the build.
