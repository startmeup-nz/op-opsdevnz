"""
OpsDev.nz namespace package.

This module exposes helpers for resolving secrets and integrating with OctoDNS.
"""

from .onepassword import SecretError, get_secret  # noqa: F401
