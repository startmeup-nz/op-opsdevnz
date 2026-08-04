"""Tests for the .env.refs.* loader."""

import os

from op_opsdevnz.env import load_refs


def test_load_refs_loads_existing_file(tmp_path, monkeypatch):
    refs = tmp_path / ".env.refs.staging"
    refs.write_text("OP_TEST_LOADED_REF=op://Vault/Item/Field\n")
    monkeypatch.delenv("OP_TEST_LOADED_REF", raising=False)

    load_refs(path=str(refs))
    try:
        assert os.getenv("OP_TEST_LOADED_REF") == "op://Vault/Item/Field"
    finally:
        os.environ.pop("OP_TEST_LOADED_REF", None)


def test_load_refs_missing_file_is_a_noop(tmp_path):
    load_refs(path=str(tmp_path / "does-not-exist"))


def test_load_refs_default_filename(tmp_path, monkeypatch):
    refs = tmp_path / ".env.refs.staging"
    refs.write_text("OP_TEST_DEFAULT_REF=op://Vault/Item/Field\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OP_TEST_DEFAULT_REF", raising=False)

    load_refs("staging")
    try:
        assert os.getenv("OP_TEST_DEFAULT_REF") == "op://Vault/Item/Field"
    finally:
        os.environ.pop("OP_TEST_DEFAULT_REF", None)
