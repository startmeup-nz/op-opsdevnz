import subprocess

import pytest

from op_opsdevnz.onepassword import SecretError, get_secret, resolve_secret


def test_requires_reference():
    with pytest.raises(SecretError):
        get_secret()


def test_env_override_wins(monkeypatch):
    monkeypatch.setenv("OVERRIDE", "from-env")
    resolution = resolve_secret(
        secret_ref="op://Vault/Item/Field",
        env_override="OVERRIDE",
        prefer_cli=True,
    )
    assert resolution.value == "from-env"
    assert resolution.source == "env"


def test_prefer_cli_uses_cli(monkeypatch):
    monkeypatch.setenv("METANAME_TOKEN_REF", "op://Vault/Item/Field")

    monkeypatch.setattr("opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout="cli-secret\n", stderr="")

    monkeypatch.setattr("opsdevnz.onepassword.subprocess.run", _fake_run)

    resolution = resolve_secret(
        secret_ref_env="METANAME_TOKEN_REF",
        prefer_cli=True,
    )
    assert resolution.value == "cli-secret"
    assert resolution.source == "cli"


def test_sdk_used_when_available(monkeypatch):
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    monkeypatch.delenv("METANAME_TOKEN", raising=False)

    class _FakeSecrets:
        def resolve(self, reference: str) -> str:
            assert reference == "op://Vault/Item/Field"
            return "sdk-secret"

    class _FakeClient:
        secrets = _FakeSecrets()

    class _FakeOnePassword:
        @classmethod
        def from_environment(cls):
            return _FakeClient()

    monkeypatch.setattr("opsdevnz.onepassword.OnePassword", _FakeOnePassword, raising=False)
    monkeypatch.setattr("opsdevnz.onepassword.shutil.which", lambda _: None)

    resolution = resolve_secret(secret_ref="op://Vault/Item/Field")
    assert resolution.value == "sdk-secret"
    assert resolution.source == "sdk"
