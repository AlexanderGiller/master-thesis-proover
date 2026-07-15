from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest

from proof_checker_demo import check_proof_file
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus, BinaryConnective, Quantifier


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MutationCase:
    name: str
    seed_proof: Path
    problem_file: Path
    expected_valid: bool
    expected_issue_bucket: str | None
    mutate: Callable[[str], str]


def _run_mutation_case(tmp_path: Path, case: MutationCase):
    mutated_text = case.mutate(case.seed_proof.read_text(encoding="utf-8"))
    mutated_proof = tmp_path / f"{case.name}.s"
    mutated_proof.write_text(mutated_text, encoding="utf-8")

    result = check_proof_file(str(mutated_proof), str(case.problem_file))

    assert result["all_ok"] is case.expected_valid
    if case.expected_issue_bucket is None:
        assert result["axiom_issues"] == {}
        assert result["negated_conjecture_issues"] == {}
        assert result["skolem_issues"] == {}
    else:
        assert result[case.expected_issue_bucket], (
            f"Expected issues in bucket {case.expected_issue_bucket}, got: {result}"
        )


SEED_COR001 = ROOT / "examples" / "correct" / "COR001+1.s"
PROBLEM_COR001 = ROOT / "examples" / "correct" / "Problems" / "COR001+1.p"
SEED_COR002 = ROOT / "examples" / "correct" / "COR002+1.s"
PROBLEM_COR002 = ROOT / "examples" / "correct" / "Problems" / "COR002+1.p"
SEED_COR003 = ROOT / "examples" / "correct" / "COR003+1.s"
PROBLEM_COR003 = ROOT / "examples" / "correct" / "Problems" / "COR003+1.p"


CASES = [
    MutationCase(
        name="baseline_cor003_is_valid",
        seed_proof=SEED_COR003,
        problem_file=PROBLEM_COR003,
        expected_valid=True,
        expected_issue_bucket=None,
        mutate=lambda text: text,
    ),
    MutationCase(
        name="axiom_reference_name_is_wrong",
        seed_proof=SEED_COR002,
        problem_file=PROBLEM_COR002,
        expected_valid=False,
        expected_issue_bucket="axiom_issues",
        mutate=lambda text: text.replace(
            "file('Problems/COR002+1.p',ax1)",
            "file('Problems/COR002+1.p',ax_missing)",
            1,
        ),
    ),
    MutationCase(
        name="negated_conjecture_status_is_wrong",
        seed_proof=SEED_COR001,
        problem_file=PROBLEM_COR001,
        expected_valid=False,
        expected_issue_bucket="negated_conjecture_issues",
        mutate=lambda text: text.replace("status(cth)", "status(thm)", 1),
    ),
    MutationCase(
        name="duplicate_skolem_symbol_is_detected",
        seed_proof=SEED_COR003,
        problem_file=PROBLEM_COR003,
        expected_valid=False,
        expected_issue_bucket="skolem_issues",
        mutate=lambda text: text.replace(
            "new_symbols(skolem, [sK1]), skolemize(Groom, sK1(Marriage))",
            "new_symbols(skolem, [sK0]), skolemize(Groom, sK0(Marriage))",
            1,
        ).replace(
            "in_love(sK1(Marriage), sK0(Marriage))",
            "in_love(sK0(Marriage), sK0(Marriage))",
            1,
        ),
    ),
    MutationCase(
        name="wrong_skolem_result_formula_is_detected",
        seed_proof=SEED_COR003,
        problem_file=PROBLEM_COR003,
        expected_valid=False,
        expected_issue_bucket="skolem_issues",
        mutate=lambda text: text.replace(
            "in_love(sK1(Marriage), sK0(Marriage))",
            "in_love(Marriage, sK0(Marriage))",
            1,
        ),
    ),
]


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_guided_mutation_cases_have_known_oracles(tmp_path, case):
    """Guided fuzzing / mutation testing with explicit expected outcomes.

    This is intentionally not unrestricted random fuzzing. Instead, we start from a
    known-correct seed proof and apply one small mutation whose expected outcome is
    known in advance:

    - keep proof valid, or
    - force one specific checker family to fail.

    This avoids the oracle problem because each mutation carries its expected label.
    """
    _run_mutation_case(tmp_path, case)


