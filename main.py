"""Comprehensive proof checker for selected proof-step validations."""

import argparse
import csv
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty

from src.checker.dependency_checker import (
    check_conjecture_not_assumed,
    check_no_circular_dependencies,
)
from src.checker.file_dir import check_axiom_provenance
from src.checker.clausal_checker import (
    check_paramodulation,
    check_reflexivity,
    check_resolution,
    check_rewrite,
    check_transitivity,
)
from src.checker.existential_gen_checker import check_existential_gen
from src.checker.external_atp_checker import status_allows_atp, validate_step_with_atp
from src.checker.formula_utils import collect_function_symbols
from src.checker.instantiate_checker import check_instantiate
from src.checker.junction_checker import check_commute, check_excluded_middle, check_weaken
from src.checker.negated_conjecture_checker import check_negated_conjecture
from src.checker.propositional_checker import (
    check_conjunction,
    check_modus_ponens,
    check_split_conjunct,
)
from src.checker.skolem_checker import SkolemizationIssue, check_skolemization
from src.checker.structural_checker import (
    check_copy,
    check_double_negation,
    check_duplicate,
    check_remove_double_negation,
    check_rename_variable,
)
from src.deep_recursion import run_with_larger_stack
from src.parser.parser import load_proof, parse_file
from src.var_mapping import FormulaRole, InferenceStatus
from src.scoring.scoring import ProofScorer, print_scoring_summary

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
    - Verify modus_ponens, conjunction, and split_conjunct steps
    - Verify copy, duplicate, rename_variable, double_negation, and
      remove_double_negation steps
    - Verify resolution, paramodulation, reflexivity, transitivity, and
      rewrite steps
    - Verify skolemization steps

    Returns a dict of issue maps and an 'all_ok' status.
    """
    problem_formulas = {f.name: f for f in parse_file(problem_path)}
    proof = load_proof(proof_path)
    steps_by_name = _build_step_index(proof.steps)

    circular_dependency_issues = {}
    for issue in check_no_circular_dependencies(proof.steps):
        circular_dependency_issues.setdefault(issue.step_name, []).append(issue.reason)
    for issue in check_conjecture_not_assumed(proof.steps):
        circular_dependency_issues.setdefault(issue.step_name, []).append(issue.reason)

    axiom_issues = {}
    conjecture_issues = {}
    negated_conjecture_issues = {}
    instantiate_issues = {}
    existential_gen_issues = {}
    modus_ponens_issues = {}
    conjunction_issues = {}
    split_conjunct_issues = {}
    copy_issues = {}
    duplicate_issues = {}
    rename_variable_issues = {}
    double_negation_issues = {}
    remove_double_negation_issues = {}
    weaken_issues = {}
    commute_issues = {}
    excluded_middle_issues = {}
    resolution_issues = {}
    paramodulation_issues = {}
    reflexivity_issues = {}
    transitivity_issues = {}
    rewrite_issues = {}
    skolem_issues = {}
    external_atp_issues = {}

    # Track conjectures for negation checking
    conjectures = {name: step for name, step in steps_by_name.items() if step.role == "conjecture"}

    # Function/constant symbols already defined in the problem file: any
    # Skolem symbol introduced later in the proof must not reuse one of these,
    # since it is required to be a genuinely fresh symbol.
    pre_existing_function_symbols: set[str] = set()
    for formula in problem_formulas.values():
        pre_existing_function_symbols |= collect_function_symbols(formula.formula)

    seen_skolem_symbols: set[str] = set()

    for step in proof.steps:
        if step.role == "axiom":
            issues = check_axiom_provenance(step, problem_formulas, problem_path)
            if issues:
                axiom_issues[step.name] = [it.reason for it in issues]

        elif step.role == "conjecture":
            issues = check_axiom_provenance(
                step, problem_formulas, problem_path, expected_role=FormulaRole.CONJECTURE
            )
            if issues:
                conjecture_issues[step.name] = [it.reason for it in issues]

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
        elif step.inference and step.inference.rule in {
            "modus_ponens",
            "conjunction",
            "split_conjunct",
        }:
            rule = step.inference.rule
            parent_names = step.inference.parents
            target_issues = {
                "modus_ponens": modus_ponens_issues,
                "conjunction": conjunction_issues,
                "split_conjunct": split_conjunct_issues,
            }[rule]
            expected_count = 1 if rule == "split_conjunct" else 2
            if len(parent_names) != expected_count:
                target_issues[step.name] = [
                    f"{rule} requires exactly {expected_count} parent(s)"
                ]
                continue
            parents = [steps_by_name.get(name) for name in parent_names]
            if any(parent is None for parent in parents):
                missing = [name for name, parent in zip(parent_names, parents) if parent is None]
                target_issues[step.name] = [f"Parent step(s) not found: {', '.join(missing)}"]
                continue
            if rule == "modus_ponens":
                issues = check_modus_ponens(step, parents[0], parents[1])
            elif rule == "conjunction":
                issues = check_conjunction(step, parents[0], parents[1])
            else:
                issues = check_split_conjunct(step, parents[0])
            if issues:
                target_issues[step.name] = [it.reason for it in issues]
        elif step.inference and step.inference.rule in {
            "copy",
            "duplicate",
            "rename_variable",
            "double_negation",
            "remove_double_negation",
        }:
            rule = step.inference.rule
            parent_names = step.inference.parents
            target_issues = {
                "copy": copy_issues,
                "duplicate": duplicate_issues,
                "rename_variable": rename_variable_issues,
                "double_negation": double_negation_issues,
                "remove_double_negation": remove_double_negation_issues,
            }[rule]
            expected_count = 2 if rule == "duplicate" else 1
            if len(parent_names) != expected_count:
                target_issues[step.name] = [
                    f"{rule} requires exactly {expected_count} parent(s)"
                ]
                continue
            parents = [steps_by_name.get(name) for name in parent_names]
            if any(parent is None for parent in parents):
                missing = [name for name, parent in zip(parent_names, parents) if parent is None]
                target_issues[step.name] = [f"Parent step(s) not found: {', '.join(missing)}"]
                continue
            if rule == "copy":
                issues = check_copy(step, parents[0])
            elif rule == "duplicate":
                issues = check_duplicate(step, parents[0], parents[1])
            elif rule == "rename_variable":
                issues = check_rename_variable(step, parents[0])
            elif rule == "double_negation":
                issues = check_double_negation(step, parents[0])
            else:
                issues = check_remove_double_negation(step, parents[0])
            if issues:
                target_issues[step.name] = [it.reason for it in issues]
        elif step.inference and step.inference.rule == "excluded_middle":
            issues = check_excluded_middle(step)
            metadata_ok = step.inference.rule == "excluded_middle" and step.inference.status == InferenceStatus.THM
            if issues and metadata_ok:
                # The syntactic check only covers the standard shape of this
                # rule (phi | ~phi, possibly with phi itself flattened into
                # several disjuncts). Fall back to the external ATP before
                # reporting a failure so unusual-but-valid variants aren't
                # rejected as false negatives.
                valid, note = validate_step_with_atp(step.formula, [])
                if not valid:
                    excluded_middle_issues[step.name] = [it.reason for it in issues]
            elif issues:
                excluded_middle_issues[step.name] = [it.reason for it in issues]
        elif step.inference and step.inference.rule in {"weaken", "commute"} and len(step.inference.parents) == 1:
            rule = step.inference.rule
            target_issues = {"weaken": weaken_issues, "commute": commute_issues}[rule]
            parent_name = step.inference.parents[0]
            parent = steps_by_name.get(parent_name)
            if parent is None:
                target_issues[step.name] = [f"Parent step not found: {parent_name}"]
                continue
            issues = check_weaken(step, parent) if rule == "weaken" else check_commute(step, parent)
            metadata_ok = step.inference.rule == rule and step.inference.status == InferenceStatus.THM
            if issues and metadata_ok:
                # The syntactic check only covers the common/simple shape of this
                # rule (OR-prefix weakening / 2-operand swap). Fall back to the
                # external ATP for the rarer, more general uses (e.g. weaken used
                # for existential generalization) before reporting a failure, so
                # we don't produce false negatives on valid but unusual steps.
                valid, note = validate_step_with_atp(step.formula, [parent.formula])
                if not valid:
                    target_issues[step.name] = [it.reason for it in issues]
            elif issues:
                target_issues[step.name] = [it.reason for it in issues]
        elif (
            step.inference
            and step.inference.rule == "resolution"
            and len(step.inference.parents) == 2
        ):
            parent_names = step.inference.parents
            parents = [steps_by_name.get(name) for name in parent_names]
            if any(parent is None for parent in parents):
                missing = [name for name, parent in zip(parent_names, parents) if parent is None]
                resolution_issues[step.name] = [f"Parent step(s) not found: {', '.join(missing)}"]
            else:
                issues = check_resolution(step, parents[0], parents[1])
                if issues:
                    resolution_issues[step.name] = [it.reason for it in issues]
        elif (
            step.inference
            and step.inference.rule == "paramodulation"
            and len(step.inference.parents) == 2
        ):
            parent_names = step.inference.parents
            parents = [steps_by_name.get(name) for name in parent_names]
            if any(parent is None for parent in parents):
                missing = [name for name, parent in zip(parent_names, parents) if parent is None]
                paramodulation_issues[step.name] = [f"Parent step(s) not found: {', '.join(missing)}"]
            else:
                issues = check_paramodulation(step, parents[0], parents[1])
                if issues:
                    paramodulation_issues[step.name] = [it.reason for it in issues]
        elif (
            step.inference
            and step.inference.rule == "reflexivity"
            and len(step.inference.parents) == 1
        ):
            parent = steps_by_name.get(step.inference.parents[0])
            if parent is None:
                reflexivity_issues[step.name] = [f"Parent step '{step.inference.parents[0]}' not found"]
            else:
                issues = check_reflexivity(step, parent)
                if issues:
                    reflexivity_issues[step.name] = [it.reason for it in issues]
        elif (
            step.inference
            and step.inference.rule == "transitivity"
            and len(step.inference.parents) == 2
        ):
            parent_names = step.inference.parents
            parents = [steps_by_name.get(name) for name in parent_names]
            if any(parent is None for parent in parents):
                missing = [name for name, parent in zip(parent_names, parents) if parent is None]
                transitivity_issues[step.name] = [f"Parent step(s) not found: {', '.join(missing)}"]
            else:
                issues = check_transitivity(step, parents[0], parents[1])
                if issues:
                    transitivity_issues[step.name] = [it.reason for it in issues]
        elif (
            step.inference
            and step.inference.rule == "rewrite"
            and len(step.inference.parents) == 1
        ):
            parent = steps_by_name.get(step.inference.parents[0])
            if parent is None:
                rewrite_issues[step.name] = [f"Parent step '{step.inference.parents[0]}' not found"]
            else:
                issues = check_rewrite(step, parent)
                if issues:
                    rewrite_issues[step.name] = [it.reason for it in issues]
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
                    if sym in pre_existing_function_symbols:
                        issues.append(
                            SkolemizationIssue(
                                step.name,
                                f"Skolem symbol '{sym}' is not fresh: it is already used as a "
                                "function/constant symbol in the problem file",
                            )
                        )
                    elif sym in seen_skolem_symbols:
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
        elif step.inference:
            external_atp_issues[step.name] = [
                f"No checker available for rule '{step.inference.rule}' with status '{step.inference.status}'"
            ]
        elif step.role not in {FormulaRole.AXIOM, FormulaRole.CONJECTURE} and step.raw_source is None:
            external_atp_issues[step.name] = [
                "Step has no justification: expected inference(...) or source(...) annotation"
            ]


    all_ok = (
        not circular_dependency_issues
        and not axiom_issues
        and not conjecture_issues
        and not negated_conjecture_issues
        and not instantiate_issues
        and not existential_gen_issues
        and not modus_ponens_issues
        and not conjunction_issues
        and not split_conjunct_issues
        and not copy_issues
        and not duplicate_issues
        and not rename_variable_issues
        and not double_negation_issues
        and not remove_double_negation_issues
        and not weaken_issues
        and not commute_issues
        and not excluded_middle_issues
        and not resolution_issues
        and not paramodulation_issues
        and not reflexivity_issues
        and not transitivity_issues
        and not rewrite_issues
        and not skolem_issues
        and not external_atp_issues
    )

    return {
        "circular_dependency_issues": circular_dependency_issues,
        "axiom_issues": axiom_issues,
        "conjecture_issues": conjecture_issues,
        "negated_conjecture_issues": negated_conjecture_issues,
        "instantiate_issues": instantiate_issues,
        "existential_gen_issues": existential_gen_issues,
        "modus_ponens_issues": modus_ponens_issues,
        "conjunction_issues": conjunction_issues,
        "split_conjunct_issues": split_conjunct_issues,
        "copy_issues": copy_issues,
        "duplicate_issues": duplicate_issues,
        "rename_variable_issues": rename_variable_issues,
        "double_negation_issues": double_negation_issues,
        "remove_double_negation_issues": remove_double_negation_issues,
        "weaken_issues": weaken_issues,
        "commute_issues": commute_issues,
        "excluded_middle_issues": excluded_middle_issues,
        "resolution_issues": resolution_issues,
        "paramodulation_issues": paramodulation_issues,
        "reflexivity_issues": reflexivity_issues,
        "transitivity_issues": transitivity_issues,
        "rewrite_issues": rewrite_issues,
        "skolem_issues": skolem_issues,
        "external_atp_issues": external_atp_issues,
        "all_ok": all_ok,
    }


def _check_proof_worker(proof_path: str, problem_path: str, result_queue: Queue) -> None:
    """Run proof checking in a subprocess and return result through a queue."""
    try:
        result = run_with_larger_stack(lambda: check_proof_file(proof_path, problem_path))
        result_queue.put(("result", result))
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

        if result["circular_dependency_issues"]:
            print("\n[FAIL] Circular Dependency Issues:")
            for name, reasons in result["circular_dependency_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] No circular dependencies detected")

        if result["axiom_issues"]:
            print("\n[FAIL] Axiom Provenance Issues:")
            for name, reasons in result["axiom_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All axioms verified correctly")

        if result["conjecture_issues"]:
            print("\n[FAIL] Conjecture Provenance Issues:")
            for name, reasons in result["conjecture_issues"].items():
                for reason in reasons:
                    print(f"  - {name}: {reason}")
        else:
            print("\n[OK] All conjectures verified correctly")

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

        for key, label in (
            ("modus_ponens_issues", "Modus Ponens"),
            ("conjunction_issues", "Conjunction"),
            ("split_conjunct_issues", "Split Conjunct"),
            ("copy_issues", "Copy"),
            ("duplicate_issues", "Duplicate"),
            ("rename_variable_issues", "Rename Variable"),
            ("double_negation_issues", "Double Negation"),
            ("remove_double_negation_issues", "Remove Double Negation"),
            ("weaken_issues", "Weaken"),
            ("commute_issues", "Commute"),
            ("excluded_middle_issues", "Excluded Middle"),
            ("resolution_issues", "Resolution"),
            ("paramodulation_issues", "Paramodulation"),
            ("reflexivity_issues", "Reflexivity"),
            ("transitivity_issues", "Transitivity"),
            ("rewrite_issues", "Rewrite"),
        ):
            if result[key]:
                print(f"\n[FAIL] {label} Issues:")
                for name, reasons in result[key].items():
                    for reason in reasons:
                        print(f"  - {name}: {reason}")
            else:
                print(f"\n[OK] All {label.lower()} steps verified correctly")

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


ISSUE_SUMMARY_COLUMNS = (
    ("circular_dependency_issues", "Circular dependency"),
    ("axiom_issues", "Axiom"),
    ("conjecture_issues", "Conjecture"),
    ("negated_conjecture_issues", "Negated conjecture"),
    ("instantiate_issues", "Instantiate"),
    ("existential_gen_issues", "Existential gen"),
    ("modus_ponens_issues", "Modus ponens"),
    ("conjunction_issues", "Conjunction"),
    ("split_conjunct_issues", "Split conjunct"),
    ("copy_issues", "Copy"),
    ("duplicate_issues", "Duplicate"),
    ("rename_variable_issues", "Rename variable"),
    ("double_negation_issues", "Double negation"),
    ("remove_double_negation_issues", "Remove double negation"),
    ("weaken_issues", "Weaken"),
    ("commute_issues", "Commute"),
    ("excluded_middle_issues", "Excluded middle"),
    ("resolution_issues", "Resolution"),
    ("paramodulation_issues", "Paramodulation"),
    ("reflexivity_issues", "Reflexivity"),
    ("transitivity_issues", "Transitivity"),
    ("rewrite_issues", "Rewrite"),
    ("skolem_issues", "Skolemization"),
    ("external_atp_issues", "External ATP"),
)


def summarize_issues(details: dict | None, status: str) -> str:
    """Return a concise description of failed checks for a proof result."""
    if details is None:
        return "Timeout" if status == "Timeout" else "Checker error"

    failures = [
        f"{label} ({len(details[key])})"
        for key, label in ISSUE_SUMMARY_COLUMNS
        if details.get(key)
    ]
    return ", ".join(failures) if failures else "-"


def print_prv_results_table(results: list[tuple[str, str, dict | None]]) -> None:
    """Print one summary row for each checked PRV proof."""
    if not results:
        return

    headers = ("Proof", "Status", "Failed checks")
    rows = [
        (proof_name, status, summarize_issues(details, status))
        for proof_name, status, details in results
    ]
    widths = [
        max(len(headers[column]), *(len(row[column]) for row in rows))
        for column in range(len(headers))
    ]
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    print("\nResults by PRV file")
    print(separator)
    print(
        "| "
        + " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
        + " |"
    )
    print(separator)
    for row in rows:
        print(
            "| "
            + " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
            + " |"
        )
    print(separator)


def parse_cli_args() -> argparse.Namespace:
    """Parse optional command-line arguments while preserving the all-files default."""
    parser = argparse.ArgumentParser(
        description="Verify one proof file or, without arguments, all ProoVer2026 proofs."
    )
    parser.add_argument(
        "proof",
        nargs="?",
        help="Proof file to verify, e.g. ProoVer2026\\PRV038+1.s",
    )
    parser.add_argument(
        "-p",
        "--problem",
        help="Problem file matching the proof; inferred from the proof filename if omitted.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=PER_PROOF_TIMEOUT_SECONDS,
        help=f"Timeout in seconds (default: {PER_PROOF_TIMEOUT_SECONDS:g}).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    base = Path(__file__).parent
    args = parse_cli_args()

    if args.proof:
        proof_path = Path(args.proof)
        if not proof_path.is_absolute():
            proof_path = Path.cwd() / proof_path
        proof_path = proof_path.resolve()

        if args.problem:
            problem_path = Path(args.problem)
            if not problem_path.is_absolute():
                problem_path = Path.cwd() / problem_path
            problem_path = problem_path.resolve()
        else:
            problem_path = proof_path.parent / "Problems" / f"{proof_path.stem}.p"

        if not proof_path.is_file():
            raise SystemExit(f"Proof file not found: {proof_path}")
        if not problem_path.is_file():
            raise SystemExit(f"Problem file not found: {problem_path}")
        if args.timeout <= 0:
            raise SystemExit("Timeout must be greater than zero.")

        status, _ = report_proof_check(str(proof_path), str(problem_path), args.timeout)
        raise SystemExit(0 if status == "VerifiedGood" else 1)

    prover_directory = base / "ProoVer2026"
    all_pairs = collect_example_pairs(prover_directory)
    all_pairs.sort(key=lambda pair: Path(pair[0]).name)

    # Initialize scorer with expected results
    expected_file = base / "PRV_expected.csv"
    scorer = ProofScorer(str(expected_file))
    
    
    total = len(all_pairs)
    verified_count = 0
    not_verified_count = 0
    timeout_count = 0
    axiom_failure_count = 0
    conjecture_failure_count = 0
    negated_conjecture_failure_count = 0
    instantiate_failure_count = 0
    existential_gen_failure_count = 0
    modus_ponens_failure_count = 0
    conjunction_failure_count = 0
    split_conjunct_failure_count = 0
    copy_failure_count = 0
    duplicate_failure_count = 0
    rename_variable_failure_count = 0
    double_negation_failure_count = 0
    remove_double_negation_failure_count = 0
    weaken_failure_count = 0
    commute_failure_count = 0
    excluded_middle_failure_count = 0
    resolution_failure_count = 0
    paramodulation_failure_count = 0
    reflexivity_failure_count = 0
    transitivity_failure_count = 0
    rewrite_failure_count = 0
    skolem_failure_count = 0
    external_atp_failure_count = 0
    prv_results = []
    scoring_results = []

    if total == 0:
        print("No proof/problem pairs found in ProoVer2026")
    else:
        for proof_sub_path, problem_sub_path in all_pairs:
            status, details = report_proof_check(proof_sub_path, problem_sub_path)
            proof_name = Path(proof_sub_path).name
            
            prv_results.append((proof_name, status, details))
            
            # Score the proof
            score_result = scorer.score_proof(proof_name, status, details)
            scoring_results.append(score_result)
            
            if status == "VerifiedGood":
                verified_count += 1
            elif status == "Timeout":
                timeout_count += 1
            else:
                not_verified_count += 1

            if details is not None:
                axiom_failure_count += len(details["axiom_issues"])
                conjecture_failure_count += len(details["conjecture_issues"])
                negated_conjecture_failure_count += len(details["negated_conjecture_issues"])
                instantiate_failure_count += len(details["instantiate_issues"])
                existential_gen_failure_count += len(details["existential_gen_issues"])
                modus_ponens_failure_count += len(details["modus_ponens_issues"])
                conjunction_failure_count += len(details["conjunction_issues"])
                split_conjunct_failure_count += len(details["split_conjunct_issues"])
                copy_failure_count += len(details["copy_issues"])
                duplicate_failure_count += len(details["duplicate_issues"])
                rename_variable_failure_count += len(details["rename_variable_issues"])
                double_negation_failure_count += len(details["double_negation_issues"])
                remove_double_negation_failure_count += len(
                    details["remove_double_negation_issues"]
                )
                weaken_failure_count += len(details["weaken_issues"])
                commute_failure_count += len(details["commute_issues"])
                excluded_middle_failure_count += len(details["excluded_middle_issues"])
                resolution_failure_count += len(details["resolution_issues"])
                paramodulation_failure_count += len(details["paramodulation_issues"])
                reflexivity_failure_count += len(details["reflexivity_issues"])
                transitivity_failure_count += len(details["transitivity_issues"])
                rewrite_failure_count += len(details["rewrite_issues"])
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
    print(f"  Conjecture verification: {conjecture_failure_count}")
    print(f"  Negated conjecture: {negated_conjecture_failure_count}")
    print(f"  Instantiate: {instantiate_failure_count}")
    print(f"  Existential gen: {existential_gen_failure_count}")
    print(f"  Modus ponens: {modus_ponens_failure_count}")
    print(f"  Conjunction: {conjunction_failure_count}")
    print(f"  Split conjunct: {split_conjunct_failure_count}")
    print(f"  Copy: {copy_failure_count}")
    print(f"  Duplicate: {duplicate_failure_count}")
    print(f"  Rename variable: {rename_variable_failure_count}")
    print(f"  Double negation: {double_negation_failure_count}")
    print(f"  Remove double negation: {remove_double_negation_failure_count}")
    print(f"  Weaken: {weaken_failure_count}")
    print(f"  Commute: {commute_failure_count}")
    print(f"  Excluded middle: {excluded_middle_failure_count}")
    print(f"  Resolution: {resolution_failure_count}")
    print(f"  Paramodulation: {paramodulation_failure_count}")
    print(f"  Reflexivity: {reflexivity_failure_count}")
    print(f"  Transitivity: {transitivity_failure_count}")
    print(f"  Rewrite: {rewrite_failure_count}")
    print(f"  Skolemization: {skolem_failure_count}")
    print(f"  External ATP: {external_atp_failure_count}")
    print_prv_results_table(prv_results)

    # Print scoring summary
    if scoring_results:
        scoring_summary = scorer.calculate_score_summary(scoring_results)
        print_scoring_summary(scoring_summary)
        
        # Export results to CSV
        output_csv = base / "src" / "results" / "ProoVer2026_results.csv"
        scorer.export_results_to_csv(scoring_results, str(output_csv))
        print(f"\nScoring results exported to: {output_csv}")
