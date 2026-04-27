"""Tests for opsdevnz.octodns_hooks module."""

import pytest

from opsdevnz.octodns_hooks import resolve


def test_resolve_with_reference(monkeypatch):
    """resolve() should pass reference directly to get_secret."""
    calls = []

    def _fake_get_secret(**kwargs):
        calls.append(kwargs)
        return "resolved-secret"

    monkeypatch.setattr("opsdevnz.octodns_hooks.opsdevnz_get_secret", _fake_get_secret)

    result = resolve("METANAME_API_TOKEN", reference="op://Vault/Item/Field")
    assert result == "resolved-secret"
    assert calls[-1]["secret_ref"] == "op://Vault/Item/Field"
    assert calls[-1]["env_override"] == "METANAME_API_TOKEN"
    assert calls[-1]["prefer_cli"] is True


def test_resolve_without_reference_uses_env(monkeypatch):
    """resolve() without reference should build secret_ref_env from name."""
    calls = []

    def _fake_get_secret(**kwargs):
        calls.append(kwargs)
        return "env-resolved-secret"

    monkeypatch.setattr("opsdevnz.octodns_hooks.opsdevnz_get_secret", _fake_get_secret)

    result = resolve("METANAME_API_TOKEN")
    assert result == "env-resolved-secret"
    assert calls[-1]["secret_ref_env"] == "METANAME_API_TOKEN_REF"
    assert calls[-1]["env_override"] == "METANAME_API_TOKEN"
    assert calls[-1]["prefer_cli"] is True


def test_resolve_propagates_secret_error(monkeypatch):
    """resolve() should propagate SecretError from get_secret."""

    from opsdevnz.onepassword import SecretError

    def _fake_get_secret(**kwargs):
        raise SecretError("resolution failed")

    monkeypatch.setattr("opsdevnz.octodns_hooks.opsdevnz_get_secret", _fake_get_secret)

    with pytest.raises(SecretError, match="resolution failed"):
        resolve("MISSING_TOKEN")


def test_resolve_with_custom_name(monkeypatch):
    """resolve() should handle different secret names correctly."""
    calls = []

    def _fake_get_secret(**kwargs):
        calls.append(kwargs)
        return "token-value"

    monkeypatch.setattr("opsdevnz.octodns_hooks.opsdevnz_get_secret", _fake_get_secret)

    result = resolve("MY_CUSTOM_SECRET")
    assert result == "token-value"
    assert calls[-1]["secret_ref_env"] == "MY_CUSTOM_SECRET_REF"
    assert calls[-1]["env_override"] == "MY_CUSTOM_SECRET"


def test_resolve_with_explicit_reference_overrides_env(monkeypatch):
    """resolve() with explicit reference should pass it as secret_ref."""
    calls = []

    def _fake_get_secret(**kwargs):
        calls.append(kwargs)
        return "ref-value"

    monkeypatch.setattr("opsdevnz.octodns_hooks.opsdevnz_get_secret", _fake_get_secret)

    result = resolve("SOME_TOKEN", reference="op://Custom/Vault/Field")
    assert result == "ref-value"
    # When reference is provided, it's passed as secret_ref
    assert calls[-1]["secret_ref"] == "op://Custom/Vault/Field"
    assert "secret_ref_env" not in calls[-1]