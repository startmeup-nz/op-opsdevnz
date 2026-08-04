"""Tests for the op-opsdevnz console CLI."""

import subprocess

import pytest

from op_opsdevnz.__main__ import _mask, main
from op_opsdevnz.onepassword import DEFAULT_CLI_TIMEOUT


def test_version_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert "op-opsdevnz" in capsys.readouterr().out


def test_resolve_masks_by_default(monkeypatch, capsys):
    monkeypatch.setenv("OVERRIDE", "super-secret-value-123")

    assert main(["resolve", "--ref", "op://V/I/F", "--env-override", "OVERRIDE"]) == 0
    out = capsys.readouterr().out
    assert out.strip() == "********"
    assert "super-secret-value-123" not in out


def test_resolve_no_mask_prints_value(monkeypatch, capsys):
    monkeypatch.setenv("OVERRIDE", "super-secret-value-123")

    assert (
        main(["resolve", "--ref", "op://V/I/F", "--env-override", "OVERRIDE", "--no-mask"]) == 0
    )
    assert capsys.readouterr().out.strip() == "super-secret-value-123"


def test_resolve_show_source_reports_env(monkeypatch, capsys):
    monkeypatch.setenv("OVERRIDE", "value")

    assert (
        main(["resolve", "--ref", "op://V/I/F", "--env-override", "OVERRIDE", "--show-source"])
        == 0
    )
    captured = capsys.readouterr()
    assert captured.out.strip() == "********"
    assert "[source] env" in captured.err


def test_resolve_via_cli_shows_cli_source(monkeypatch, capsys):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr(
        "op_opsdevnz.onepassword.subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="cli-secret\n", stderr=""),
    )

    assert main(["resolve", "--ref", "op://V/I/F", "--prefer-cli", "--show-source"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "********"
    assert "[source] cli" in captured.err


def test_resolve_error_returns_2_with_sanitized_message(monkeypatch, capsys):
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.delenv("UNSET_REF", raising=False)

    assert main(["resolve", "--ref-env", "UNSET_REF"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Error:" in captured.err


def test_mask_reveals_nothing():
    assert _mask("super-secret-value-123") == "********"
    assert _mask("ab") == "********"
    assert _mask("x") == "********"
    assert _mask("") == "(empty)"
    assert _mask("   ") == "(empty)"


def test_mask_constant_length_hides_secret_length():
    masked = {_mask("a" * n) for n in (1, 8, 64)}
    assert masked == {"********"}


def test_cli_timeout_default_is_the_shared_constant(monkeypatch, capsys):
    """The CLI --timeout default and the resolver default must not drift."""
    captured = {}

    def _run(*args, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(args, 0, stdout="cli-secret\n", stderr="")

    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr("op_opsdevnz.onepassword.shutil.which", lambda _: "/usr/bin/op")
    monkeypatch.setattr("op_opsdevnz.onepassword.subprocess.run", _run)

    assert main(["resolve", "--ref", "op://V/I/F", "--prefer-cli"]) == 0
    assert captured["timeout"] == DEFAULT_CLI_TIMEOUT
    capsys.readouterr()  # drain masked output
