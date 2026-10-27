"""Tests for scoring, performance tracking, provenance of non-axiom inputs, and the timeout wrapper."""

import csv
import sys
import time
from pathlib import Path

import main
from main import check_proof_file, check_proof_file_with_timeout
from src.performance.performance import PerformanceTracker, print_performance_table
from src.scoring import score_proofs
from src.scoring.scoring import ProofScorer, ScoringResult, print_scoring_summary

ROOT = Path(__file__).resolve().parents[1]

PROBLEM = """fof(a1, axiom, ![X]: (p(X) => q(X))).
fof(a2, {a2_role}, p(a)).
fof(c1, conjecture, q(a)).
"""

PROOF = """fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/T.p', a1)).
fof(a2, {a2_role}, p(a), file('Problems/T.p', a2)).
fof(c1, conjecture, q(a), file('Problems/T.p', c1)).
fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).
fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).
fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).
"""


def _write_pair(tmp_path: Path, proof_role: str, problem_role: str) -> tuple[str, str]:
    (tmp_path / "Problems").mkdir(exist_ok=True)
    problem = tmp_path / "Problems" / "T.p"
    proof = tmp_path / "T.s"
    problem.write_text(PROBLEM.format(a2_role=problem_role), encoding="utf-8")
    proof.write_text(PROOF.format(a2_role=proof_role), encoding="utf-8")
    return str(proof), str(problem)


# --- provenance of formulas with other input roles -------------------------------


def test_hypothesis_matching_the_problem_is_accepted(tmp_path):
    proof, problem = _write_pair(tmp_path, "hypothesis", "hypothesis")
    result = check_proof_file(proof, problem)
    assert result["axiom_issues"] == {}
    assert result["verdict"] == "VerifiedGood"


def test_hypothesis_with_wrong_role_is_rejected(tmp_path):
    proof, problem = _write_pair(tmp_path, "hypothesis", "axiom")
    result = check_proof_file(proof, problem)
    assert "a2" in result["axiom_issues"]
    assert result["verdict"] == "VerifiedBad"


def test_hypothesis_not_in_problem_is_rejected(tmp_path):
    proof, problem = _write_pair(tmp_path, "hypothesis", "hypothesis")
    Path(proof).write_text(
        Path(proof).read_text(encoding="utf-8").replace("p(a), file", "p(b), file"),
        encoding="utf-8",
    )
    result = check_proof_file(proof, problem)
    assert any("alpha-equivalent" in r for r in result["axiom_issues"].get("a2", []))
    assert result["verdict"] == "VerifiedBad"


def test_introduced_formula_cannot_be_verified(tmp_path):
    proof, problem = _write_pair(tmp_path, "axiom", "axiom")
    text = Path(proof).read_text(encoding="utf-8")
    text = text.replace(
        "fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).",
        "fof(f1, plain, q(a), introduced(definition, [])).",
    )
    Path(proof).write_text(text, encoding="utf-8")
    result = check_proof_file(proof, problem)
    assert "f1" in result["external_atp_issues"]
    assert result["verdict"] != "VerifiedGood"


# --- timeout wrapper ---------------------------------------------------------------


def _slow_worker(proof_path, problem_path, result_queue, debug=False):
    time.sleep(5)


def _dying_worker(proof_path, problem_path, result_queue, debug=False):
    sys.exit(3)


def test_timeout_wrapper_returns_result(tmp_path):
    proof, problem = _write_pair(tmp_path, "axiom", "axiom")
    outcome, payload = check_proof_file_with_timeout(proof, problem, 30)
    assert outcome == "result"
    assert payload["verdict"] == "VerifiedGood"


def test_timeout_wrapper_reports_error_for_missing_file(tmp_path):
    outcome, payload = check_proof_file_with_timeout(
        str(tmp_path / "missing.s"), str(tmp_path / "missing.p"), 30
    )
    assert outcome == "error"


def test_timeout_wrapper_reports_timeout(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "_check_proof_worker", _slow_worker)
    start = time.perf_counter()
    outcome, _ = check_proof_file_with_timeout("x.s", "x.p", 0.5)
    assert outcome == "timeout"
    assert time.perf_counter() - start < 4


def test_timeout_wrapper_reports_dead_worker(monkeypatch):
    monkeypatch.setattr(main, "_check_proof_worker", _dying_worker)
    outcome, payload = check_proof_file_with_timeout("x.s", "x.p", 30)
    assert outcome == "error"
    assert "exited" in payload


# --- scoring -------------------------------------------------------------------------


def test_points_follow_the_competition_scheme():
    assert ScoringResult("a", "CORRECT", "VerifiedGood").points == 1
    assert ScoringResult("a", "INCORRECT", "VerifiedBad").points == 2
    assert ScoringResult("a", "CORRECT", "VerifiedBad").points == -1
    assert ScoringResult("a", "INCORRECT", "VerifiedGood").points == -10
    assert ScoringResult("a", "INCORRECT", "Unknown").points == 0
    assert ScoringResult("a", "CORRECT", "Timeout").points == 0
    assert ScoringResult("a", "EDGE", "VerifiedGood").points == 0


def test_error_categories_are_counted():
    details = {"skolem_issues": {"s1": ["x"], "s2": ["y"]}, "axiom_issues": {}}
    res = ScoringResult("a", "INCORRECT", "VerifiedBad", details)
    assert res.get_error_categories() == {"Skolemization": 2}
    assert ScoringResult("a", "INCORRECT", "Unknown", details).get_error_categories() == {}


def test_expected_results_loader_accepts_all_layouts(tmp_path):
    f = tmp_path / "exp.csv"
    f.write_text(
        "proof,expected_status,description\n"
        "PRV001+1.s,CORRECT,x\n"
        "TST001+1.s,ax01,INCORRECT,y\n"
        "EXT001+1.s,resolution,EDGE,z\n"
        "\n",
        encoding="utf-8",
    )
    scorer = ProofScorer(str(f))
    assert scorer.expected == {
        "PRV001+1.s": "CORRECT",
        "TST001+1.s": "INCORRECT",
        "EXT001+1.s": "EDGE",
    }
    assert scorer.score_proof("missing.s", "VerifiedGood").expected_status == "UNKNOWN"
    assert ProofScorer(str(tmp_path / "nope.csv")).expected == {}


def test_summary_and_export(tmp_path, capsys):
    scorer = ProofScorer(str(ROOT / "src" / "scoring" / "PRV_expected.csv"))
    results = [
        ScoringResult("v", "CORRECT", "VerifiedGood"),
        ScoringResult("i", "INCORRECT", "VerifiedBad", {"axiom_issues": {"a": ["r"]}}),
        ScoringResult("u", "INCORRECT", "Unknown"),
        ScoringResult("w", "CORRECT", "VerifiedBad", {"skolem_issues": {"s": ["r"]}}),
        ScoringResult("t", "CORRECT", "Timeout"),
        ScoringResult("e", "CORRECT", "Crash"),
    ]
    summary = scorer.calculate_score_summary(results)
    assert summary["total_points"] == 1 + 2 + 0 - 1 + 0 + 0
    assert summary["max_points"] == 1 + 2 + 2 + 1 + 1 + 1
    assert summary["min_points"] == -1 - 10 - 10 - 1 - 1 - 1
    assert summary["unknown"] == 1 and summary["timeout"] == 1 and summary["error"] == 1
    assert dict(summary["error_categories"]) == {"Skolemization": 1}
    assert scorer.calculate_score_summary([]) == {}

    out = tmp_path / "sub" / "report.csv"
    scorer.export_results_to_csv(results, str(out))
    rows = list(csv.reader(out.open(encoding="utf-8")))
    assert rows[0][0] == "Proof" and len(rows) == len(results) + 1

    print_scoring_summary(summary)
    print_scoring_summary({})
    printed = capsys.readouterr().out
    assert "SCORING SUMMARY" in printed and "No results to summarize" in printed


def test_score_proofs_script(tmp_path, monkeypatch, capsys):
    results = tmp_path / "results.csv"
    results.write_text(
        "Proof,Expected,Actual\nPRV000+1.s,CORRECT,VerifiedGood\nPRV001+1.s,INCORRECT,VerifiedBad\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.csv"
    monkeypatch.setattr(sys, "argv", ["score_proofs", "-r", str(results), "-o", str(output)])
    score_proofs.main()
    assert output.exists()
    assert "Total Points:          3" in capsys.readouterr().out

    loaded = tmp_path / "status.csv"
    loaded.write_text("Proof,Status\nA.s,VerifiedGood\n", encoding="utf-8")
    assert score_proofs.load_verification_results(str(loaded)) == {"A.s": "VerifiedGood"}

    monkeypatch.setattr(sys, "argv", ["score_proofs", "-r", str(tmp_path / "missing.csv")])
    score_proofs.main()
    assert "Results file not found" in capsys.readouterr().out


# --- performance tracking --------------------------------------------------------------


def test_performance_tracker(capsys):
    tracker = PerformanceTracker()
    assert tracker.get_summary_by_operation() == {}
    assert tracker.get_overall_summary()["total_measurements"] == 0
    tracker.print_summary()
    print_performance_table(tracker)

    tracker.start()
    m = tracker.stop("parse")
    assert m.wc_time >= 0 and "parse" in repr(m)
    tracker.add_measurement("parse", 0.5, 0.4)
    tracker.add_measurement("check", 1.0, 0.9)

    by_op = tracker.get_summary_by_operation()
    assert by_op["parse"]["count"] == 2 and by_op["check"]["count"] == 1
    overall = tracker.get_overall_summary()
    assert overall["total_measurements"] == 3

    tracker.print_summary()
    tracker.print_summary(operation_filter="check")
    tracker.print_summary(operation_filter="nothing")
    print_performance_table(tracker)
    assert len(tracker.get_all_measurements()) == 3
    out = capsys.readouterr().out
    assert "PERFORMANCE SUMMARY" in out and "No measurements found" in out

    tracker.reset()
    assert tracker.get_all_measurements() == []
    try:
        tracker.stop()
    except ValueError:
        pass
    else:
        raise AssertionError("stop() without start() must raise")
