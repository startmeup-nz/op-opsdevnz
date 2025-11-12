"""
OpsDev.nz namespace package.

This module exposes helpers for resolving secrets and integrating with OctoDNS.
"""

from .onepassword import (  # noqa: F401
    SecretError,
    SecretResolution,
    get_secret,
    resolve_secret,
)

__all__ = ["SecretError", "SecretResolution", "get_secret", "resolve_secret"]
