"""
op_opsdevnz — 1Password secret resolution for OpsDev.nz automation.

Exposes helpers for resolving ``op://`` secrets via the 1Password Service
Account SDK, with a conditional ``op`` CLI fallback for local development.
"""

from .onepassword import (  # noqa: F401
    SdkAuthError,
    SdkNotConfiguredError,
    SecretError,
    SecretResolution,
    get_secret,
    resolve_secret,
)

__all__ = [
    "SdkAuthError",
    "SdkNotConfiguredError",
    "SecretError",
    "SecretResolution",
    "get_secret",
    "resolve_secret",
]
