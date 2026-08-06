"""Comprehensive proof checker for selected proof-step validations."""

from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty

from src.checker.file_dir import check_axiom_provenance
from src.checker.existential_gen_checker import check_existential_gen
from src.checker.external_atp_checker import status_allows_atp, validate_step_with_atp
from src.checker.instantiate_checker import check_instantiate
from src.checker.negated_conjecture_checker import check_negated_conjecture
from src.checker.skolem_checker import SkolemizationIssue, check_skolemization
from src.parser.parser import load_proof, parse_file

PER_PROOF_TIMEOUT_SECONDS = 30.0


def _build_step_index(steps):
    index = {}
    for step in steps:
        index.setdefault(step.name, step)
    return index


def check_proof_file(proof_path: str, problem_path: str) -> dict:
    """Check a proof file for correctness:

    - Verify axiom provenance and alpha-equivalence
    - Verify negated_conjecture steps
    - Verify instantiate and existential_gen steps
    - Verify skolemization steps

    Returns a dict of issue maps and an 'all_ok' status.
    """
    problem_formulas = {f.name: f for f in parse_file(problem_path)}
    proof = load_proof(proof_path)
    steps_by_name = _build_step_index(proof.steps)

    axiom_issues = {}
    negated_conjecture_issues = {}
    instantiate_issues = {}
    existential_gen_issues = {}
    skolem_issues = {}
    external_atp_issues = {}

    # Track conjectures for negation checking
    conjectures = {name: step for name, step in steps_by_name.items() if step.role == "conjecture"}

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
                    negated_conjecture_issues[step.name] = [
                        f"Parent conjecture '{parent_name}' not found"
                    ]
            else:
                negated_conjecture_issues[step.name] = [
                    "No parent conjecture specified in inference"
                ]
        elif step.inference and step.inference.rule == "instantiate":
            if not step.inference.parents:
                instantiate_issues[step.name] = ["No parent specified for instantiate step"]
                continue
            parent_name = step.inference.parents[0]
            parent = steps_by_name.get(parent_name)
            if parent is None:
                instantiate_issues[step.name] = [f"Parent step '{parent_name}' not found"]
                continue
            issues = check_instantiate(step, parent)
            if issues:
                instantiate_issues[step.name] = [it.reason for it in issues]
        elif step.inference and step.inference.rule == "existential_gen":
            if not step.inference.parents:
                existential_gen_issues[step.name] = [
                    "No parent specified for existential_gen step"
                ]
                continue
            parent_name = step.inference.parents[0]
            parent = steps_by_name.get(parent_name)
            if parent is None:
                existential_gen_issues[step.name] = [f"Parent step '{parent_name}' not found"]
                continue
            issues = check_existential_gen(step, parent)
            if issues:
                existential_gen_issues[step.name] = [it.reason for it in issues]
        elif step.inference and status_allows_atp(step.inference.status):
            parent_names = step.inference.parents or []
            parent_steps = []
            missing_parents = []
            for parent_name in parent_names:
                parent = steps_by_name.get(parent_name)
                if parent is None:
                    missing_parents.append(parent_name)
                else:
                    parent_steps.append(parent.formula)
            if missing_parents:
                external_atp_issues[step.name] = [
                    f"Parent step(s) not found: {', '.join(missing_parents)}"
                ]
            else:
                valid, note = validate_step_with_atp(step.formula, parent_steps)
                if not valid:
                    external_atp_issues[step.name] = [f"External ATP rejected step: {note}"]
        # Skolemization steps: often role is 'plain' but inference.rule == 'skolemize'
        elif step.inference and step.inference.rule == "skolemize":
            # Find parent step by name (first parent)
            if not step.inference.parents:
                skolem_issues[step.name] = ["No parent specified for skolemize step"]
                continue
            parent_name = step.inference.parents[0]
            parent = steps_by_name.get(parent_name)
            if parent is None:
                skolem_issues[step.name] = [f"Parent step '{parent_name}' not found"]
                continue

            issues = check_skolemization(step, parent)

            # Uniqueness check: any introduced skolem symbols must not have been seen before
            if step.inference.new_symbols:
                for sym in step.inference.new_symbols:
                    if sym in seen_skolem_symbols:
                        issues.append(
                            SkolemizationIssue(
                                step.name, f"Skolem symbol '{sym}' was already introduced earlier"
                            )
                        )
                # add all introduced symbols to seen set
                for sym in step.inference.new_symbols:
                    seen_skolem_symbols.add(sym)

            if issues:
                skolem_issues[step.name] = [it.reason for it in issues]

    all_ok = (
        not axiom_issues
        and not negated_conjecture_issues
        and not instantiate_issues
        and not existential_gen_issues
        and not skolem_issues
        and not external_atp_issues
    )

    return {
        "axiom_issues": axiom_issues,
        "negated_conjecture_issues": negated_conjecture_issues,
        "instantiate_issues": instantiate_issues,
        "existential_gen_issues": existential_gen_issues,
        "skolem_issues": skolem_issues,
        "external_atp_issues": external_atp_issues,
        "all_ok": all_ok,
    }


def _check_proof_worker(proof_path: str, problem_path: str, result_queue: Queue) -> None:
    """Run proof checking in a subprocess and return result through a queue."""
    try:
        result_queue.put(("result", check_proof_file(proof_path, problem_path)))
    except Exception as exc:
        result_queue.put(("error", f"{type(exc).__name__}: {exc}"))


def check_proof_file_with_timeout(
    proof_path: str, problem_path: str, timeout_seconds: float
) -> tuple[str, dict | str | None]:
    """Run proof checking with a wall-clock timeout.

    Returns:
        ("result", dict) on success,
        ("timeout", None) on timeout,
        ("error", str) on runtime failure.
    """
    result_queue: Queue = Queue()
    process = Process(target=_check_proof_worker, args=(proof_path, problem_path, result_queue))
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        return "timeout", None

    try:
        return result_queue.get_nowait()
    except Empty:
        return "error", f"Proof checking process exited with code {process.exitcode}"


def report_proof_check(
    proof_path: str, problem_path: str, timeout_seconds: float = PER_PROOF_TIMEOUT_SECONDS
) -> tuple[str, dict | None]:
    """Run the proof check, print a report, and return the overall status and details."""
    print(f"\n{'='*70}")
    print(f"Checking proof: {proof_path}")
    print(f"Against problem: {problem_path}")
    print(f"{'='*70}")

    outcome, payload = check_proof_file_with_timeout(proof_path, problem_path, timeout_seconds)

    if outcome == "timeout":
        print(f"\n[TIMEOUT] Exceeded wall-clock limit of {timeout_seconds:.1f} seconds")
        print("\n% SZS status Timeout")
        return "Timeout", None
    elif outcome == "error":
        print(f"\n[ERROR] Failed to check proof: {payload}")
        print("\n% SZS status VerifiedBad")
        return "VerifiedBad", None
    else:
        result = payload

        if result["axiom_issues"]:
            print("\n[FAIL] Axiom Provenance Issues:")
            for name, reasons in result["axiom_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All axioms verified correctly")

        if result["negated_conjecture_issues"]:
            print("\n[FAIL] Negated Conjecture Issues:")
            for name, reasons in result["negated_conjecture_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All negated conjectures verified correctly")

        if result["instantiate_issues"]:
            print("\n[FAIL] Instantiate Issues:")
            for name, reasons in result["instantiate_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All instantiate steps verified correctly")

        if result["existential_gen_issues"]:
            print("\n[FAIL] Existential Gen Issues:")
            for name, reasons in result["existential_gen_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All existential generalization steps verified correctly")

        if result["skolem_issues"]:
            print("\n[FAIL] Skolem Issues:")
            for name, reasons in result["skolem_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All skolem steps verified correctly")

        if result["external_atp_issues"]:
            print("\n[FAIL] External ATP Issues:")
            for name, reasons in result["external_atp_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All ATP-checked steps verified correctly")

        if result["all_ok"]:
            print("\n% SZS status VerifiedGood")
            return "VerifiedGood", result

        print("\n% SZS status VerifiedBad")
        return "VerifiedBad", result


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
    base = Path(__file__).parent
    prover_directory = base / "ProoVer2026"
    all_pairs = collect_example_pairs(prover_directory)
    all_pairs.sort(key=lambda pair: Path(pair[0]).name)

    total = len(all_pairs)
    verified_count = 0
    not_verified_count = 0
    timeout_count = 0
    axiom_failure_count = 0
    negated_conjecture_failure_count = 0
    instantiate_failure_count = 0
    existential_gen_failure_count = 0
    skolem_failure_count = 0
    external_atp_failure_count = 0

    if total == 0:
        print("No proof/problem pairs found in ProoVer2026")
    else:
        for proof_sub_path, problem_sub_path in all_pairs:
            status, details = report_proof_check(proof_sub_path, problem_sub_path)
            if status == "VerifiedGood":
                verified_count += 1
            elif status == "Timeout":
                timeout_count += 1
            else:
                not_verified_count += 1

            if details is not None:
                axiom_failure_count += len(details["axiom_issues"])
                negated_conjecture_failure_count += len(details["negated_conjecture_issues"])
                instantiate_failure_count += len(details["instantiate_issues"])
                existential_gen_failure_count += len(details["existential_gen_issues"])
                skolem_failure_count += len(details["skolem_issues"])
                external_atp_failure_count += len(details["external_atp_issues"])

    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"Total proofs checked: {total}")
    print(f"VerifiedGood: {verified_count}")
    print(f"VerifiedBad: {not_verified_count}")
    print(f"Timeout: {timeout_count}")
    print("Failed steps:")
    print(f"  Axiom verification: {axiom_failure_count}")
    print(f"  Negated conjecture: {negated_conjecture_failure_count}")
    print(f"  Instantiate: {instantiate_failure_count}")
    print(f"  Existential gen: {existential_gen_failure_count}")
    print(f"  Skolemization: {skolem_failure_count}")
    print(f"  External ATP: {external_atp_failure_count}")
