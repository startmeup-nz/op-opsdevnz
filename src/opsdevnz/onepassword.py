"""
1Password helpers for OpsDev.nz.

Provides a thin wrapper around the official Service Account SDK with an optional
fallback to the `op` CLI so local developers can resolve `op://` references
without additional tooling.
"""

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal, Optional

try:
    # Official SDK (requires OP_SERVICE_ACCOUNT_TOKEN)
    from onepassword import OnePassword
except Exception:  # pragma: no cover
    OnePassword = None


class SecretError(RuntimeError):
    """Raised when secret resolution fails."""


SecretSource = Literal["env", "sdk", "cli"]


@dataclass
class SecretResolution:
    """Result of resolving a secret, including which resolver was used."""

    value: str
    source: SecretSource


def _resolve_via_sdk(secret_ref: str) -> str:
    if OnePassword is None:
        raise SecretError("onepassword-sdk not installed")
    if not os.getenv("OP_SERVICE_ACCOUNT_TOKEN"):
        raise SecretError("OP_SERVICE_ACCOUNT_TOKEN is not set for SDK usage")
    op = OnePassword.from_environment()
    value = op.secrets.resolve(secret_ref)
    if not value:
        raise SecretError(f"Secret reference resolved to empty value: {secret_ref}")
    return value


def _resolve_via_cli(secret_ref: str, timeout: float = 10.0) -> str:
    if not shutil.which("op"):
        raise SecretError("1Password CLI 'op' not found in PATH")
    try:
        proc = subprocess.run(
            ["op", "read", secret_ref],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        value = proc.stdout.strip()
        if not value:
            raise SecretError(f"Empty value returned by 'op read' for {secret_ref}")
        return value
    except subprocess.CalledProcessError as exc:
        raise SecretError(f"op read failed: {exc.stderr or exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise SecretError("Timed out calling 'op read'") from exc


def resolve_secret(
    *,
    secret_ref_env: Optional[str] = None,
    secret_ref: Optional[str] = None,
    env_override: Optional[str] = None,
    prefer_cli: bool = False,
    timeout: float = 10.0,
) -> SecretResolution:
    """Resolve a 1Password secret and report which resolver produced it.

    Resolution order:
        1. Return ``env_override`` when set (local overrides, CI tests).
        2. Resolve the provided ``secret_ref`` or the value from
           ``secret_ref_env`` (must point to an ``op://`` reference).
        3. Use the Service Account SDK by default, falling back to the CLI when
           ``prefer_cli`` is true or the SDK path fails and the CLI is available.
    """

    if env_override and (value := os.getenv(env_override)):
        return SecretResolution(value=value, source="env")

    reference = secret_ref or (os.getenv(secret_ref_env) if secret_ref_env else None)
    if not reference or not reference.startswith("op://"):
        raise SecretError("A valid 1Password secret reference is required (op://Vault/Item/Field)")

    if prefer_cli:
        try:
            value = _resolve_via_cli(reference, timeout=timeout)
            return SecretResolution(value=value, source="cli")
        except SecretError as cli_error:
            # fall back to SDK when available so CI/service-account flows still work
            try:
                value = _resolve_via_sdk(reference)
                return SecretResolution(value=value, source="sdk")
            except SecretError:
                # raise original CLI error to preserve context for local devs
                raise cli_error from None

    try:
        value = _resolve_via_sdk(reference)
        return SecretResolution(value=value, source="sdk")
    except SecretError:
        if shutil.which("op"):
            value = _resolve_via_cli(reference, timeout=timeout)
            return SecretResolution(value=value, source="cli")
        raise


def get_secret(
    *,
    secret_ref_env: Optional[str] = None,
    secret_ref: Optional[str] = None,
    env_override: Optional[str] = None,
    prefer_cli: bool = False,
    timeout: float = 10.0,
) -> str:
    """Backward-compatible helper that returns only the secret value."""

    return resolve_secret(
        secret_ref_env=secret_ref_env,
        secret_ref=secret_ref,
        env_override=env_override,
        prefer_cli=prefer_cli,
        timeout=timeout,
    ).value
