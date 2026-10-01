from pathlib import Path

from proof_checker_demo import check_proof_file

ROOT = Path(__file__).resolve().parents[1]


def test_prv097_reports_unchecked_trivial_esa_step():
    result = check_proof_file(
        str(ROOT / "ProoVer2026" / "PRV097+1.s"),
        str(ROOT / "ProoVer2026" / "Problems" / "PRV097+1.p"),
    )

    assert "s" in result["external_atp_issues"]
    assert any(
        "No checker available for rule 'trivial' with status 'esa'" in reason
        for reason in result["external_atp_issues"]["s"]
    )


def test_prv036_reports_unjustified_hypothesis_step():
    result = check_proof_file(
        str(ROOT / "ProoVer2026" / "PRV036+1.s"),
        str(ROOT / "ProoVer2026" / "Problems" / "PRV036+1.p"),
    )

    assert "h" in result["external_atp_issues"]
    assert any(
        "Step has no justification" in reason for reason in result["external_atp_issues"]["h"]
    )


def test_prv039_reports_unjustified_plain_step():
    result = check_proof_file(
        str(ROOT / "ProoVer2026" / "PRV039+1.s"),
        str(ROOT / "ProoVer2026" / "Problems" / "PRV039+1.p"),
    )

    assert "s" in result["external_atp_issues"]
    assert any(
        "Step has no justification" in reason for reason in result["external_atp_issues"]["s"]
    )


