from main import check_proof_file
from src.parser.ast_nodes import AnnotatedFormula, Atom, InferenceRecord, ProofFile, StatusInfo
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus


def test_external_atp_unknown_creates_issue(monkeypatch):
    step = AnnotatedFormula(
        name="s1",
        role=FormulaRole.PLAIN,
        formula=Atom("p", []),
        inference=InferenceRecord(
            rule=InferenceRule.DEDUCTION,
            info=[StatusInfo(InferenceStatus.THM)],
            parents=[],
        ),
    )

    monkeypatch.setattr("main.parse_file", lambda _path: [])
    monkeypatch.setattr(
        "main.load_proof", lambda _path: ProofFile(problem_ref="dummy", steps=[step])
    )
    monkeypatch.setattr(
        "main.validate_step_with_atp",
        lambda step_formula, premise_formulas, timeout_seconds: (
            "unknown",
            "ATP executable not found",
        ),
    )

    result = check_proof_file("dummy.s", "dummy.p")

    assert "s1" in result["external_atp_issues"]
    assert any(
        "External ATP could not validate step" in reason
        for reason in result["external_atp_issues"]["s1"]
    )
    assert result["all_ok"] is False
    # the toy proof also lacks a final $false, so the verdict is a definite VerifiedBad
    assert result["verdict"] == "VerifiedBad"
