"""Async helpers for resolving 1Password secrets via the official SDK.

Event-loop callers must use this module directly: the synchronous entry points
in :mod:`op_opsdevnz.onepassword` bridge the SDK with ``asyncio.run()`` and
fail when invoked from a running loop.
"""

import asyncio
import os
from typing import Optional

from .onepassword import SecretError, _resolve_ref_async


async def resolve_secret_async(secret_ref: str) -> str:
    """Resolve an ``op://`` reference via the Service Account SDK (async API).

    Raises:
        SdkNotConfiguredError: SDK not installed or no token configured.
        SdkAuthError: SDK was configured but authenticate/resolve failed.
    """
    return await _resolve_ref_async(secret_ref)


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
