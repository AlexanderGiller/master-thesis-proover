from pathlib import Path

from main import check_proof_file

ROOT = Path(__file__).resolve().parents[1]
_DIR = {"PRV": "PRV", "TST": "Test"}  # proof prefix -> subdirectory of ProoVer2026


def _check(name: str) -> dict:
    return check_proof_file(
        str(ROOT / "ProoVer2026" / _DIR[name[:3]] / f"{name}.s"),
        str(ROOT / "ProoVer2026" / _DIR[name[:3]] / "Problems" / f"{name}.p"),
    )


def test_proof_without_false_is_rejected():
    """EIF: TST036 never derives $false."""
    result = _check("TST036+1")
    assert "<proof>" in result["no_false_issues"]
    assert not result["all_ok"]


def test_duplicate_step_name_is_rejected():
    """NAU: TST044 defines f1 twice."""
    result = _check("TST044+1")
    assert "f1" in result["duplicate_name_issues"]
    assert not result["all_ok"]


def test_correct_proof_has_neither_issue():
    result = _check("PRV013+1")
    assert not result["no_false_issues"]
    assert not result["duplicate_name_issues"]
