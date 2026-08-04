"""Tests for the async SDK API in op_opsdevnz.onepassword_sdk."""

import asyncio

import pytest
from test_onepassword import REF, _FailingAuthClient, _FakeClient

from op_opsdevnz.onepassword import SdkAuthError, SecretError
from op_opsdevnz.onepassword_sdk import get_secret_from_ref_env, resolve_secret_async


def test_resolve_secret_async_uses_client_flow(monkeypatch):
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    monkeypatch.setattr("op_opsdevnz.onepassword.Client", _FakeClient)

    assert asyncio.run(resolve_secret_async(REF)) == "sdk-secret"


def test_resolve_secret_async_propagates_auth_failure(monkeypatch):
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    monkeypatch.setattr("op_opsdevnz.onepassword.Client", _FailingAuthClient)

    with pytest.raises(SdkAuthError):
        asyncio.run(resolve_secret_async(REF))


def test_get_secret_from_ref_env_env_override_wins(monkeypatch):
    monkeypatch.setenv("MY_SECRET", "override-value")
    assert get_secret_from_ref_env("MISSING_REF", env_override="MY_SECRET") == "override-value"


def test_get_secret_from_ref_env_missing_env_var(monkeypatch):
    monkeypatch.delenv("MISSING_REF", raising=False)
    with pytest.raises(SecretError, match="MISSING_REF is not set"):
        get_secret_from_ref_env("MISSING_REF")


def test_get_secret_from_ref_env_requires_op_reference(monkeypatch):
    monkeypatch.setenv("BAD_REF", "not-an-op-reference")
    with pytest.raises(SecretError, match="must contain an op:// reference"):
        get_secret_from_ref_env("BAD_REF")


def test_get_secret_from_ref_env_resolves(monkeypatch):
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    monkeypatch.setenv("GOOD_REF", REF)
    monkeypatch.setattr("op_opsdevnz.onepassword.Client", _FakeClient)

    assert get_secret_from_ref_env("GOOD_REF") == "sdk-secret"
