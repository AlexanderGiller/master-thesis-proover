from pathlib import Path

import pytest

from src.checker.file_dir import check_axiom_provenance
from src.parser.parser import load_proof, parse_file
from src.var_mapping import FormulaRole, InferenceRule, InferenceStatus, BinaryConnective, Quantifier


EXAMPLES_DIR = Path("examples/correct")


@pytest.mark.parametrize("proof_path", sorted(EXAMPLES_DIR.glob("*.s")))
def test_example_proofs_verify(proof_path):
    """For each example proof, verify that axiom steps match their problem files."""
    problem_dir = proof_path.parent / "Problems"
    problem_file = problem_dir / f"{proof_path.stem}.p"
    assert problem_file.exists(), f"Problem file not found for {proof_path.name}: {problem_file}"

    problem_formulas = {f.name: f for f in parse_file(str(problem_file))}
    proof = load_proof(str(proof_path))

    issues = []
    for step in proof.steps:
        if step.role != FormulaRole.AXIOM:
            continue
        step_issues = check_axiom_provenance(step, problem_formulas, str(problem_file))
        for it in step_issues:
            issues.append(f"{proof_path.name}:{it.formula_name}: {it.reason}")

    assert not issues, "Found provenance/alpha-equivalence issues:\n" + "\n".join(issues)

