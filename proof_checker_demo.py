"""Comprehensive proof checker that verifies axiom provenance and negated conjecture correctness."""

from pathlib import Path

from src.checker.file_dir import check_axiom_provenance
from src.checker.negated_conjecture_checker import check_negated_conjecture
from src.checker.skolem_checker import SkolemizationIssue, check_skolemization
from src.parser.parser import load_proof, parse_file


def check_proof_file(proof_path: str, problem_path: str) -> dict:
    """Check a proof file for correctness:

    - Verify axiom provenance and alpha-equivalence
    - Verify negated_conjecture steps

    Returns a dict with 'axiom_issues', 'negated_conjecture_issues', and 'all_ok' status.
    """
    problem_formulas = {f.name: f for f in parse_file(problem_path)}
    proof = load_proof(proof_path)

    axiom_issues = {}
    negated_conjecture_issues = {}
    skolem_issues = {}

    # Track conjectures for negation checking
    conjectures = {f.name: f for f in proof.steps if f.role == "conjecture"}

    seen_skolem_symbols: set[str] = set()

    for step in proof.steps:
        if step.role == "axiom":
            issues = check_axiom_provenance(step, problem_formulas, problem_path)
            if issues:
                axiom_issues[step.name] = [it.reason for it in issues]

        elif step.role == "negated_conjecture":
            # Find the parent conjecture
            if step.inference and step.inference.parents:
                parent_name = step.inference.parents[0]
                if parent_name in conjectures:
                    parent_conj = conjectures[parent_name]
                    issues = check_negated_conjecture(step, parent_conj)
                    if issues:
                        negated_conjecture_issues[step.name] = [it.reason for it in issues]
                else:
                    negated_conjecture_issues[step.name] = [f"Parent conjecture '{parent_name}' not found"]
            else:
                negated_conjecture_issues[step.name] = ["No parent conjecture specified in inference"]
        # Skolemization steps: often role is 'plain' but inference.rule == 'skolemize'
        elif step.inference and step.inference.rule == "skolemize":
            # Find parent step by name (first parent)
            if not step.inference.parents:
                skolem_issues[step.name] = ["No parent specified for skolemize step"]
                continue
            parent_name = step.inference.parents[0]
            parent = next((s for s in proof.steps if s.name == parent_name), None)
            if parent is None:
                skolem_issues[step.name] = [f"Parent step '{parent_name}' not found"]
                continue

            issues = check_skolemization(step, parent)

            # Uniqueness check: any introduced skolem symbols must not have been seen before
            if step.inference.new_symbols:
                for sym in step.inference.new_symbols:
                    if sym in seen_skolem_symbols:
                        issues.append(SkolemizationIssue(step.name, f"Skolem symbol '{sym}' was already introduced earlier"))
                # add all introduced symbols to seen set
                for sym in step.inference.new_symbols:
                    seen_skolem_symbols.add(sym)

            if issues:
                skolem_issues[step.name] = [it.reason for it in issues]



    all_ok = not axiom_issues and not negated_conjecture_issues and not skolem_issues

    return {
        "axiom_issues": axiom_issues,
        "negated_conjecture_issues": negated_conjecture_issues,
        "skolem_issues": skolem_issues,
        "all_ok": all_ok,
    }


def report_proof_check(proof_path: str, problem_path: str) -> None:
    """Run a proof check and print a formatted report."""
    print(f"\n{'='*70}")
    print(f"Checking proof: {proof_path}")
    print(f"Against problem: {problem_path}")
    print(f"{'='*70}")

    result = check_proof_file(proof_path, problem_path)

    if result["axiom_issues"]:
        print("\n❌ Axiom Provenance Issues:")
        for name, reasons in result["axiom_issues"].items():
            for reason in reasons:
                print(f"  - {name}: {reason}")
    else:
        print("\n✅ All axioms verified correctly")

    if result["negated_conjecture_issues"]:
        print("\n❌ Negated Conjecture Issues:")
        for name, reasons in result["negated_conjecture_issues"].items():
            for reason in reasons:
                print(f"  - {name}: {reason}")
    else:
        print("\n✅ All negated conjectures verified correctly")

    if result["skolem_issues"]:
        print("\n❌ Skolem Issues:")
        for name, reasons in result["skolem_issues"].items():
            for reason in reasons:
                print(f"  - {name}: {reason}")
    else:
        print("\n✅ All skolem steps verified correctly")

    if result["all_ok"]:
        print("\n% SZS status VerifiedGood")
    else:
        print("\n% SZS status VerifiedBad")


def collect_example_pairs(example_dir: Path):
    """Collect (proof_path, problem_path) pairs from an examples subdirectory.

    Looks for proof files with extension .s in the directory and pairs each with
    the corresponding problem file in the 'Problems' subfolder (same stem + .p).
    """
    pairs = []
    problems_dir = example_dir / "Problems"
    if not example_dir.exists():
        return pairs
    for proof in example_dir.glob("*.s"):
        problem = problems_dir / f"{proof.stem}.p"
        if problem.exists():
            pairs.append((str(proof), str(problem)))
        else:
            print(f"Warning: problem file not found for {proof} -> expected {problem}")
    return pairs

if __name__ == "__main__":
    # Iterate over example proofs in examples/correct and examples/incorrect

    all_pairs = []
    base = Path(__file__).parent
    for sub in ("correct", "incorrect"):
        example_directory = base / "examples" / sub
        all_pairs.extend(collect_example_pairs(example_directory))

    # iterate with a while loop as requested
    i = 0
    total = len(all_pairs)
    if total == 0:
        print("No example pairs found in examples/correct or examples/incorrect")
    while i < total:
        proof_sub_path, problem_sub_path = all_pairs[i]
        report_proof_check(proof_sub_path, problem_sub_path)
        i += 1

