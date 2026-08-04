"""Tests for the OctoDNS Metaname resolver hook."""

from op_opsdevnz import octodns_hooks


def _capture_get_secret(monkeypatch):
    calls = []

    def _fake_get_secret(**kwargs):
        calls.append(kwargs)
        return "resolved"

    monkeypatch.setattr("op_opsdevnz.octodns_hooks.op_get_secret", _fake_get_secret)
    return calls


def test_hook_prefers_cli_on_workstations_without_token(monkeypatch):
    """No service-account token: the signed-in op session is the principal."""
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    calls = _capture_get_secret(monkeypatch)

    assert octodns_hooks.resolve("METANAME_API_TOKEN") == "resolved"
    assert calls == [
        {
            "secret_ref_env": "METANAME_API_TOKEN_REF",
            "env_override": "METANAME_API_TOKEN",
            "prefer_cli": True,
        }
    ]


def test_hook_lets_sdk_run_when_token_configured(monkeypatch):
    """Token set: SDK path runs first (same principal as the CLI in CI)."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    calls = _capture_get_secret(monkeypatch)

    assert octodns_hooks.resolve("METANAME_API_TOKEN") == "resolved"
    assert calls[0]["prefer_cli"] is False
    assert calls[0]["secret_ref_env"] == "METANAME_API_TOKEN_REF"


def test_hook_passes_explicit_reference_directly(monkeypatch):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    calls = _capture_get_secret(monkeypatch)

    assert octodns_hooks.resolve("METANAME_API_TOKEN", reference="op://V/I/F") == "resolved"
    assert calls == [
        {
            "secret_ref": "op://V/I/F",
            "env_override": "METANAME_API_TOKEN",
            "prefer_cli": True,
        }
    ]
