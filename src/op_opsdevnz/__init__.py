"""
Compatibility wrapper exposing opsdevnz helpers under the op_opsdevnz namespace.

Downstream code can import from ``op_opsdevnz`` while the canonical modules live
under ``opsdevnz``.
"""

from opsdevnz.onepassword import SecretError, get_secret  # noqa: F401
