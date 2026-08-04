"""
op_opsdevnz.__main__
--------------------

Implements the `op-opsdevnz` CLI for resolving 1Password secrets.
"""

import argparse
import sys
from importlib import metadata
from typing import List, Optional

from .onepassword import DEFAULT_CLI_TIMEOUT, SecretError, resolve_secret


def _mask(value: str) -> str:
    """Return a fully opaque placeholder for a secret value.

    The mask reveals nothing about the underlying value — no characters, no
    length — so default CLI output is always safe to log or paste. Use
    ``--no-mask`` to print the resolved value itself.
    """
    return "********" if (value or "").strip() else "(empty)"


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the `op-opsdevnz` CLI."""

    try:
        dist_version = metadata.version("op-opsdevnz")
    except metadata.PackageNotFoundError:
        dist_version = "0.0.0"

    parser = argparse.ArgumentParser(
        prog="op-opsdevnz",
        description="Resolve 1Password secrets (Service Account + CLI fallback)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {dist_version}",
        help="Show the installed version and exit",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    resolve = sub.add_parser("resolve", help="Resolve a secret reference")
    ref_group = resolve.add_mutually_exclusive_group(required=True)
    ref_group.add_argument("--ref", help="1Password secret reference (op://Vault/Item/Field)")
    ref_group.add_argument(
        "--ref-env",
        help="Environment variable containing the secret reference (e.g. METANAME_API_TOKEN_REF)",
    )
    resolve.add_argument(
        "--env-override",
        help="Environment variable to use as an override secret value",
    )
    resolve.add_argument(
        "--prefer-cli",
        action="store_true",
        help="Use the op CLI even if the Service Account SDK is available",
    )
    resolve.add_argument(
        "--no-mask",
        action="store_true",
        help="Print the full resolved value (default prints an opaque mask)",
    )
    resolve.add_argument(
        "--show-source",
        action="store_true",
        help="Print which resolver was used (sdk|cli|env)",
    )
    resolve.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_CLI_TIMEOUT,
        help=f"Timeout for CLI fallback in seconds (default: {DEFAULT_CLI_TIMEOUT:g})",
    )

    args = parser.parse_args(argv)

    if args.cmd == "resolve":
        try:
            resolution = resolve_secret(
                secret_ref_env=args.ref_env if args.ref_env else None,
                secret_ref=args.ref if args.ref else None,
                env_override=args.env_override,
                prefer_cli=args.prefer_cli,
                timeout=args.timeout,
            )
            value = resolution.value
            print(value if args.no_mask else _mask(value))
            if args.show_source:
                print(f"[source] {resolution.source}", file=sys.stderr)
            return 0
        except SecretError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2

    return 64  # EX_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
