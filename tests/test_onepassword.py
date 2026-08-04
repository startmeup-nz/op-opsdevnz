"""Tests for the synchronous resolver in op_opsdevnz.onepassword."""

import asyncio
import subprocess

import pytest

from op_opsdevnz.onepassword import (
    SdkAuthError,
    SdkNotConfiguredError,
    SecretError,
    get_secret,
    resolve_secret,
)

REF = "op://TestVault/TestItem/TestField"


class _FakeSecrets:
    """Mirrors onepassword.secrets.Secrets (async resolve)."""

    def __init__(self, value="sdk-secret", error=None):
        self._value = value
        self._error = error

    async def resolve(self, reference: str) -> str:
        assert reference == REF
        if self._error is not None:
            raise self._error
        return self._value


class _FakeClient:
    """Mirrors onepassword.client.Client (async authenticate classmethod)."""

    def __init__(self, secrets):
        self.secrets = secrets

    @classmethod
    async def authenticate(cls, auth: str, integration_name: str, integration_version: str):
        assert auth == "token"
        assert integration_name == "OpsDev.nz"
        assert "+" not in integration_version  # SDK rejects build metadata
        return cls(_FakeSecrets())


class _FailingAuthClient:
    """Client whose authenticate raises, like the real SDK's bare exceptions."""

    @classmethod
    async def authenticate(cls, auth: str, integration_name: str, integration_version: str):
        raise RuntimeError(f"invalid user input: rejected token for {REF}")


def _fake_cli_run(value="cli-secret\n", error=None):
    def _run(*args, **kwargs):
        if error is not None:
            raise error
        return subprocess.CompletedProcess(args, 0, stdout=value, stderr="")

    return _run


def _use_fake_sdk_client(monkeypatch, client_cls=_FakeClient):
    monkeypatch.setattr("op_opsdevnz.onepassword.Client", client_cls)


def test_sdk_contract_symbols_exist():
    """Guard: fail loudly if the installed SDK no longer exposes the targeted API.

    This is the enforcement point for the adapter contract — the SDK ships no
    usable type information for mypy (ignore_missing_imports), so only a real
    import catches a renamed or removed symbol.
    """
    import onepassword.client
    import onepassword.secrets

    assert hasattr(onepassword.client, "Client"), "onepassword.client.Client missing"
    assert hasattr(onepassword.client.Client, "authenticate"), "Client.authenticate missing"
    assert hasattr(onepassword.secrets, "Secrets"), "onepassword.secrets.Secrets missing"
    assert hasattr(onepassword.secrets.Secrets, "resolve"), "Secrets.resolve missing"


def test_requires_reference():
    with pytest.raises(SecretError):
        get_secret()


def test_rejects_non_op_reference():
    with pytest.raises(SecretError, match="valid 1Password secret reference"):
        resolve_secret(secret_ref="https://example.com/not-a-1password-ref")


def test_env_override_wins(monkeypatch):
    monkeypatch.setenv("OVERRIDE", "from-env")
    resolution = resolve_secret(
        secret_ref=REF,
        env_override="OVERRIDE",
        prefer_cli=True,
    )
    assert resolution.value == "from-env"
    assert resolution.source == "env"


def test_get_secret_returns_value_only(monkeypatch):
    monkeypatch.setenv("OVERRIDE", "from-env")
    assert get_secret(secret_ref=REF, env_override="OVERRIDE") == "from-env"


def test_sdk_resolution_via_real_client_flow(monkeypatch):
    """The SDK path drives the async Client flow through the asyncio bridge."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    _use_fake_sdk_client(monkeypatch)

    resolution = resolve_secret(secret_ref=REF)
    assert resolution.value == "sdk-secret"
    assert resolution.source == "sdk"


def test_sdk_not_configured_without_token_falls_back_to_cli(monkeypatch):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr("op_opsdevnz.onepassword.subprocess.run", _fake_cli_run())

    resolution = resolve_secret(secret_ref=REF)
    assert resolution.value == "cli-secret"
    assert resolution.source == "cli"


def test_sdk_not_installed_counts_as_not_configured(monkeypatch):
    """Import failure is a configuration state, so CLI fallback is allowed."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    monkeypatch.setattr("op_opsdevnz.onepassword.Client", None)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr("op_opsdevnz.onepassword.subprocess.run", _fake_cli_run())

    resolution = resolve_secret(secret_ref=REF)
    assert resolution.source == "cli"


def test_not_configured_and_no_cli_is_a_clear_error(monkeypatch):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: None)

    with pytest.raises(SecretError, match="OP_SERVICE_ACCOUNT_TOKEN is not set"):
        resolve_secret(secret_ref=REF)


def test_sdk_auth_failure_is_hard_fail_no_cli_fallback(monkeypatch):
    """A configured-but-failing SDK must never switch principals to the CLI."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    _use_fake_sdk_client(monkeypatch, _FailingAuthClient)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr(
        "op_opsdevnz.onepassword.subprocess.run",
        lambda *a, **k: pytest.fail("CLI must not be attempted after SDK auth failure"),
    )

    with pytest.raises(SdkAuthError):
        resolve_secret(secret_ref=REF)


def test_sdk_resolution_failure_is_hard_fail(monkeypatch):
    class _ResolveFails:
        @classmethod
        async def authenticate(cls, auth, integration_name, integration_version):
            return type("C", (), {"secrets": _FakeSecrets(error=ValueError(f"no item at {REF}"))})()

    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    _use_fake_sdk_client(monkeypatch, _ResolveFails)

    with pytest.raises(SdkAuthError):
        resolve_secret(secret_ref=REF)


def test_sdk_error_is_sanitized(monkeypatch):
    """Raw SDK messages can embed the reference or token diagnostics."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    _use_fake_sdk_client(monkeypatch, _FailingAuthClient)

    with pytest.raises(SdkAuthError) as exc_info:
        resolve_secret(secret_ref=REF)
    message = str(exc_info.value)
    assert REF not in message
    assert "invalid user input" not in message
    assert exc_info.value.__cause__ is None  # chain suppressed: tracebacks stay clean


def test_sdk_empty_value_is_hard_fail(monkeypatch):
    class _EmptyValue:
        @classmethod
        async def authenticate(cls, auth, integration_name, integration_version):
            return type("C", (), {"secrets": _FakeSecrets(value="")})()

    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    _use_fake_sdk_client(monkeypatch, _EmptyValue)

    with pytest.raises(SdkAuthError, match="empty value"):
        resolve_secret(secret_ref=REF)


def test_sync_resolver_rejects_running_event_loop(monkeypatch):
    """Hard API contract: async callers must use op_opsdevnz.onepassword_sdk."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")

    async def _call():
        resolve_secret(secret_ref=REF)

    with pytest.raises(SecretError, match="event loop"):
        asyncio.run(_call())


def test_prefer_cli_uses_cli(monkeypatch):
    monkeypatch.setenv("METANAME_TOKEN_REF", REF)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr("op_opsdevnz.onepassword.subprocess.run", _fake_cli_run())

    resolution = resolve_secret(
        secret_ref_env="METANAME_TOKEN_REF",
        prefer_cli=True,
    )
    assert resolution.value == "cli-secret"
    assert resolution.source == "cli"


def test_prefer_cli_falls_back_to_sdk(monkeypatch):
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    _use_fake_sdk_client(monkeypatch)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr(
        "op_opsdevnz.onepassword.subprocess.run",
        _fake_cli_run(error=subprocess.CalledProcessError(1, ["op"])),
    )

    resolution = resolve_secret(secret_ref=REF, prefer_cli=True)
    assert resolution.value == "sdk-secret"
    assert resolution.source == "sdk"


def test_prefer_cli_raises_original_cli_error_when_sdk_also_fails(monkeypatch):
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    _use_fake_sdk_client(monkeypatch, _FailingAuthClient)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr(
        "op_opsdevnz.onepassword.subprocess.run",
        _fake_cli_run(error=subprocess.CalledProcessError(1, ["op"])),
    )

    with pytest.raises(SecretError) as exc_info:
        resolve_secret(secret_ref=REF, prefer_cli=True)
    assert type(exc_info.value) is SecretError  # the CLI error, not an SDK subclass
    assert "exit code 1" in str(exc_info.value)


def test_cli_error_is_sanitized(monkeypatch):
    """Raw op stderr can contain the reference or session diagnostics."""
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr(
        "op_opsdevnz.onepassword.subprocess.run",
        _fake_cli_run(
            error=subprocess.CalledProcessError(
                1, ["op"], stderr=f"[ERROR] could not find item at {REF} in vault"
            )
        ),
    )

    with pytest.raises(SecretError) as exc_info:
        resolve_secret(secret_ref=REF)
    message = str(exc_info.value)
    assert REF not in message
    assert "[ERROR]" not in message
    assert "exit code 1" in message
    assert exc_info.value.__cause__ is None


def test_cli_timeout_is_reported(monkeypatch):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr(
        "op_opsdevnz.onepassword.subprocess.run",
        _fake_cli_run(error=subprocess.TimeoutExpired(cmd=["op"], timeout=3.0)),
    )

    with pytest.raises(SecretError, match="Timed out"):
        resolve_secret(secret_ref=REF, timeout=3.0)


def test_cli_empty_value_is_an_error(monkeypatch):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr("op_opsdevnz.onepassword.subprocess.run", _fake_cli_run(value="\n"))

    with pytest.raises(SecretError, match="empty value"):
        resolve_secret(secret_ref=REF)


def test_cli_missing_binary(monkeypatch):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: None)

    with pytest.raises(SecretError, match="not found in PATH"):
        resolve_secret(secret_ref=REF, prefer_cli=True)


def test_error_subclass_hierarchy():
    assert issubclass(SdkNotConfiguredError, SecretError)
    assert issubclass(SdkAuthError, SecretError)
