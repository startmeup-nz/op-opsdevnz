"""Tests for opsdevnz.env module."""

from pathlib import Path

from opsdevnz.env import load_refs


def test_load_refs_missing_file(tmp_path: Path, monkeypatch):
    """load_refs should silently skip absent files."""
    monkeypatch.chdir(tmp_path)
    # No .env.refs.staging file exists — should not raise
    load_refs(env="staging")


def test_load_refs_loads_env_file(tmp_path: Path, monkeypatch):
    """load_refs should load variables from a .env.refs file."""
    env_file = tmp_path / ".env.refs.staging"
    env_file.write_text("STAGING_VAR=loaded_value\n")
    monkeypatch.chdir(tmp_path)

    import os

    # Ensure the var is not set before
    monkeypatch.delenv("STAGING_VAR", raising=False)

    load_refs(env="staging")

    # After loading, the env var should be available via os.environ
    assert os.environ.get("STAGING_VAR") == "loaded_value"


def test_load_refs_custom_path(tmp_path: Path, monkeypatch):
    """load_refs should accept a custom path argument."""
    custom_file = tmp_path / "custom.env"
    custom_file.write_text("CUSTOM_VAR=custom_value\n")

    monkeypatch.delenv("CUSTOM_VAR", raising=False)

    load_refs(path=str(custom_file))

    import os

    assert os.environ.get("CUSTOM_VAR") == "custom_value"


def test_load_refs_does_not_override_existing(tmp_path: Path, monkeypatch):
    """load_refs should not override already-set env variables."""
    monkeypatch.setenv("EXISTING_VAR", "original")
    env_file = tmp_path / ".env.refs.test"
    env_file.write_text("EXISTING_VAR=overridden\n")
    monkeypatch.chdir(tmp_path)

    load_refs(env="test")

    import os

    # python-dotenv's load_dotenv does NOT override by default
    # so the original value should remain
    assert os.environ.get("EXISTING_VAR") == "original"


def test_load_refs_explicit_path(tmp_path: Path, monkeypatch):
    """load_refs with explicit path should load from that file."""
    env_file = tmp_path / "my-env-refs"
    env_file.write_text("MY_TEST_VAR=my_test_value\n")

    monkeypatch.delenv("MY_TEST_VAR", raising=False)

    load_refs(path=str(env_file))

    import os

    assert os.environ.get("MY_TEST_VAR") == "my_test_value"