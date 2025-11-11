import pytest

from op_opsdevnz.onepassword import SecretError, get_secret


def test_requires_reference():
    with pytest.raises(SecretError):
        get_secret()


def test_env_override_wins(monkeypatch):
    monkeypatch.setenv("OVERRIDE", "from-env")
    value = get_secret(
        secret_ref="op://Vault/Item/Field",
        env_override="OVERRIDE",
        prefer_cli=True,
    )
    assert value == "from-env"
