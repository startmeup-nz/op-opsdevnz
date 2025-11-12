"""
opsdevnz.__main__
-----------------

Implements the `op-opsdevnz` CLI for resolving 1Password secrets.
"""

import argparse
import sys
from importlib import metadata
from typing import List, Optional

from .onepassword import SecretError, resolve_secret


def _mask(value: str) -> str:
    """Return a masked representation of a secret value."""
    text = (value or "").strip()
    if not text:
        return "…" * 8
    if len(text) <= 8:
        head = text[:1]
        tail = "" if len(text) < 2 else "…" * 7
        return f"{head}{tail}"
    return f"{text[:4]}…{text[-4:]}"


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the `op-opsdevnz` CLI."""

    try:
        dist_version = metadata.version("op-opsdevnz")
    except metadata.PackageNotFoundError:
        dist_version = "0.0.0+unknown"

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
        help="Print the full value (default prints a masked preview)",
    )
    resolve.add_argument(
        "--show-source",
        action="store_true",
        help="Print which resolver was used (sdk|cli|env)",
    )
    resolve.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout for CLI fallback (seconds)",
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
