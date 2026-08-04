"""
1Password helpers for OpsDev.nz.

Provides a thin wrapper around the official Service Account SDK with a
conditional fallback to the `op` CLI so local developers can resolve `op://`
references without additional tooling.

Fallback policy (see docs/design/fallback-policy.md):

- The CLI is used only when the SDK path is *not configured* (SDK not
  installed, or ``OP_SERVICE_ACCOUNT_TOKEN`` unset), or when the caller
  explicitly passes ``prefer_cli=True``.
- Once the SDK path is configured, any failure — authentication, resolution,
  rate limit — is a hard failure. The resolver never switches credential
  principals silently.
"""

import asyncio
import os
import shutil
import subprocess
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from typing import Literal, Optional

try:
    # Official SDK (requires OP_SERVICE_ACCOUNT_TOKEN)
    from onepassword.client import Client
except ImportError:  # pragma: no cover
    Client = None


class SecretError(RuntimeError):
    """Raised when secret resolution fails."""


class SdkNotConfiguredError(SecretError):
    """The SDK path is not configured (SDK missing or no service-account token).

    Falling back to the ``op`` CLI is allowed in this state.
    """


class SdkAuthError(SecretError):
    """The SDK path is configured but failed (auth, resolution, or rate limit).

    This is a hard failure: the resolver must not fall back to the CLI and
    silently switch credential principals.
    """


SecretSource = Literal["env", "sdk", "cli"]


@dataclass
class SecretResolution:
    """Result of resolving a secret, including which resolver was used."""

    value: str
    source: SecretSource


def _package_version() -> str:
    """Return the installed distribution version, safe for SDK integration metadata.

    The SDK rejects build metadata (``+``) in the integration version, so it is
    stripped here.
    """
    try:
        version = importlib_metadata.version("op-opsdevnz")
    except importlib_metadata.PackageNotFoundError:
        return "0.0.0"
    return version.split("+")[0]


def _integration_meta() -> dict[str, str]:
    return {
        "integration_name": "OpsDev.nz",
        "integration_version": _package_version(),
    }


async def _resolve_ref_async(secret_ref: str) -> str:
    """Resolve an ``op://`` reference through the Service Account SDK.

    Raises:
        SdkNotConfiguredError: SDK not installed or no token configured.
        SdkAuthError: SDK was configured but authenticate/resolve failed.
    """
    if Client is None:
        raise SdkNotConfiguredError("onepassword-sdk is not installed")
    token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        raise SdkNotConfiguredError("OP_SERVICE_ACCOUNT_TOKEN is not set")
    try:
        client = await Client.authenticate(auth=token, **_integration_meta())
        value = await client.secrets.resolve(secret_ref)
    except Exception:
        # The SDK raises bare exceptions whose messages can embed the reference
        # or token diagnostics; never propagate them (NFR-1/NFR-2).
        raise SdkAuthError(
            "1Password SDK failed to resolve the secret "
            "(authentication, authorization, or resolution error)"
        ) from None
    if not value:
        raise SdkAuthError("1Password SDK returned an empty value for the secret reference")
    return value


def _resolve_via_sdk(secret_ref: str) -> str:
    """Synchronous bridge over the async SDK flow.

    Hard contract: must not be called from within a running event loop
    (``asyncio.run()`` fails there). Async callers use
    ``op_opsdevnz.onepassword_sdk`` directly.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_resolve_ref_async(secret_ref))
    raise SecretError(
        "resolve_secret() cannot run inside an active event loop; "
        "use the async API in op_opsdevnz.onepassword_sdk instead"
    )


def _resolve_via_cli(secret_ref: str, timeout: float = 10.0) -> str:
    op_path = shutil.which("op")
    if not op_path:
        raise SecretError("1Password CLI 'op' not found in PATH")
    try:
        proc = subprocess.run(
            [op_path, "read", secret_ref],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.CalledProcessError as exc:
        # CLI stderr can contain the reference or session diagnostics; do not
        # propagate it (NFR-1/NFR-2).
        raise SecretError(f"'op read' failed with exit code {exc.returncode}") from None
    except subprocess.TimeoutExpired as exc:
        raise SecretError(f"Timed out calling 'op read' after {timeout:g}s") from exc
    value = proc.stdout.strip()
    if not value:
        raise SecretError("'op read' returned an empty value")
    return value


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
        3. Use the Service Account SDK by default. Fall back to the CLI only
           when the SDK path is not configured (``SdkNotConfiguredError``);
           a configured-but-failing SDK (``SdkAuthError``) is a hard failure
           so credential principals never switch silently.
        4. With ``prefer_cli=True``, try the CLI first and fall back to the
           SDK when available, so CI/service-account flows still work.
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
    except SdkNotConfiguredError as sdk_error:
        # SDK path not configured: CLI fallback allowed.
        if shutil.which("op"):
            value = _resolve_via_cli(reference, timeout=timeout)
            return SecretResolution(value=value, source="cli")
        raise SecretError(
            f"{sdk_error}; the 'op' CLI is also not available"
        ) from sdk_error


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
