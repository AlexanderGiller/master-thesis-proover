import subprocess

from src.checker.external_atp_checker import validate_step_with_atp
from src.parser.ast_nodes import Atom


def _fake_formula() -> Atom:
    return Atom("p", [])


def test_validate_step_with_atp_returns_unknown_when_binary_missing(monkeypatch):
    monkeypatch.setattr("src.checker.external_atp_checker._resolve_atp_command", lambda: ["missing-atp"])

    def _raise_missing(*args, **kwargs):
        raise FileNotFoundError("missing-atp")

    monkeypatch.setattr("src.checker.external_atp_checker.subprocess.run", _raise_missing)

    valid, note = validate_step_with_atp(_fake_formula(), [], timeout_seconds=1.0)

    assert valid == "unknown"
    assert "not found" in note


def test_validate_step_with_atp_returns_unknown_on_timeout(monkeypatch):
    monkeypatch.setattr("src.checker.external_atp_checker._resolve_atp_command", lambda: ["vampire"])

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="vampire", timeout=1.0)

    monkeypatch.setattr("src.checker.external_atp_checker.subprocess.run", _raise_timeout)

    valid, note = validate_step_with_atp(_fake_formula(), [], timeout_seconds=1.0)

    assert valid == "unknown"
    assert note == "ATP timed out"


def test_validate_step_with_atp_returns_unknown_without_szs_status(monkeypatch):
    monkeypatch.setattr("src.checker.external_atp_checker._resolve_atp_command", lambda: ["vampire"])

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="no status", stderr="")

    monkeypatch.setattr("src.checker.external_atp_checker.subprocess.run", _fake_run)

    valid, note = validate_step_with_atp(_fake_formula(), [], timeout_seconds=1.0)

    assert valid == "unknown"
    assert "did not contain an SZS status" in note


def test_validate_step_with_atp_returns_true_for_theorem(monkeypatch):
    monkeypatch.setattr("src.checker.external_atp_checker._resolve_atp_command", lambda: ["vampire"])

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="% SZS status Theorem for generated problem",
            stderr="",
        )

    monkeypatch.setattr("src.checker.external_atp_checker.subprocess.run", _fake_run)

    valid, note = validate_step_with_atp(_fake_formula(), [], timeout_seconds=1.0)

    assert valid is True
    assert note == "Theorem"


def test_validate_step_with_atp_returns_false_for_countersatisfiable(monkeypatch):
    monkeypatch.setattr("src.checker.external_atp_checker._resolve_atp_command", lambda: ["vampire"])

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="% SZS status CounterSatisfiable for generated problem",
            stderr="",
        )

    monkeypatch.setattr("src.checker.external_atp_checker.subprocess.run", _fake_run)

    valid, note = validate_step_with_atp(_fake_formula(), [], timeout_seconds=1.0)

    assert valid is False
    assert note == "CounterSatisfiable"



def test_validate_step_with_atp_returns_unknown_for_prover_timeout_status(monkeypatch):
    """A prover that stops with its own time limit has no answer: not a refutation."""
    monkeypatch.setattr("src.checker.external_atp_checker._resolve_atp_command", lambda: ["vampire"])

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0], returncode=1, stdout="% SZS status Timeout for validation", stderr=""
        )

    monkeypatch.setattr("src.checker.external_atp_checker.subprocess.run", _fake_run)

    valid, note = validate_step_with_atp(_fake_formula(), [], timeout_seconds=1.0)

    assert valid == "unknown"
    assert "Timeout" in note
