"""Async helpers for resolving 1Password secrets via the official SDK."""

import asyncio
import os
from importlib import metadata as importlib_metadata
from typing import Optional

from onepassword.client import Client

from .onepassword import SecretError


def _package_version() -> str:
    try:
        return importlib_metadata.version("op-opsdevnz")
    except importlib_metadata.PackageNotFoundError:
        return "0.0.0+dev"


def _integration_meta() -> dict[str, str]:
    return {
        "integration_name": "OpsDev.nz",
        "integration_version": _package_version(),
    }


def _token() -> str:
    token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        raise SecretError("OP_SERVICE_ACCOUNT_TOKEN is not set")
    return token


async def _resolve_ref_async(secret_ref: str) -> str:
    client = await Client.authenticate(auth=_token(), **_integration_meta())
    value = await client.secrets.resolve(secret_ref)
    if not value:
        raise SecretError(f"Empty secret for reference: {secret_ref}")
    return value


def get_secret_from_ref_env(ref_env: str, *, env_override: Optional[str] = None) -> str:
    """Synchronously resolve a secret reference stored in an env var."""

    if env_override and (value := os.getenv(env_override)):
        return value
    reference = os.getenv(ref_env)
    if not reference:
        raise SecretError(f"{ref_env} is not set")
    if not reference.startswith("op://"):
        raise SecretError(f"{ref_env} must contain an op:// reference")
    return asyncio.run(_resolve_ref_async(reference))
