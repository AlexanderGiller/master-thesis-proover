"""Three-valued verdict: VerifiedGood / VerifiedBad / Unknown."""

from main import classify_verdict
from src.scoring.scoring import ScoringResult


def _result(**issues):
    keys = [
        "circular_dependency_issues", "duplicate_name_issues", "no_false_issues", "axiom_issues",
        "external_atp_issues", "skolem_issues", "resolution_issues",
    ]
    res = {k: {} for k in keys}
    res.update(issues)
    res["all_ok"] = not any(res[k] for k in keys)
    return res


def test_good_when_no_issue():
    assert classify_verdict(_result()) == "VerifiedGood"


def test_unknown_when_only_undecided_steps():
    res = _result(external_atp_issues={"s1": ["External ATP could not validate step: Timeout"]})
    assert classify_verdict(res) == "Unknown"
    res = _result(external_atp_issues={"s2": ["No checker available for rule 'trivial' with status 'thm'"]})
    assert classify_verdict(res) == "Unknown"


def test_bad_when_prover_refutes_step():
    res = _result(external_atp_issues={"s1": ["External ATP rejected step: CounterSatisfiable"]})
    assert classify_verdict(res) == "VerifiedBad"


def test_bad_when_undecided_and_refuted_mixed():
    res = _result(external_atp_issues={
        "s1": ["External ATP could not validate step: Timeout"],
        "s2": ["External ATP rejected step: CounterSatisfiable"],
    })
    assert classify_verdict(res) == "VerifiedBad"


def test_bad_when_internal_checker_fails_even_if_other_step_undecided():
    res = _result(
        resolution_issues={"s3": ["bad resolution"]},
        external_atp_issues={"s1": ["External ATP could not validate step: Timeout"]},
    )
    assert classify_verdict(res) == "VerifiedBad"


def test_unknown_scores_zero_points_for_either_expectation():
    assert ScoringResult("p", "CORRECT", "Unknown").points == 0
    assert ScoringResult("p", "INCORRECT", "Unknown").points == 0
