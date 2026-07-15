# provenance.py
from dataclasses import dataclass
from pathlib import Path

from src.checker.alpha_eq import is_alpha_equivalent
from src.parser.ast_nodes import AnnotatedFormula, FileSource
from src.var_mapping import FormulaRole


@dataclass
class ProvenanceIssue:
    formula_name: str
    reason: str


def check_axiom_provenance(
    proof_axiom: AnnotatedFormula,
    problem_axioms: dict[str, AnnotatedFormula],
    expected_problem_path: str,
) -> list[ProvenanceIssue]:
    """Checks that a proof-file axiom correctly cites the problem file it was
    imported from, and that its formula content is alpha-equivalent to the
    original axiom in that problem file."""
    issues: list[ProvenanceIssue] = []
    name = proof_axiom.name

    if not isinstance(proof_axiom.raw_source, FileSource):
        issues.append(
            ProvenanceIssue(name, "missing file(...) source directive; cannot verify provenance")
        )
        return issues
    cited_path = proof_axiom.raw_source.path
    cited_ref = proof_axiom.raw_source.ref

    # Compare by filename, not full path -- the proof file might cite
    # '/work/problem1.p' (container path) while your problem set uses a
    # different absolute path locally. Tighten this if you need exact paths.
    if Path(cited_path).name != Path(expected_problem_path).name:
        issues.append(
            ProvenanceIssue(
                name,
                f"file(...) points to '{cited_path}', expected a file named "
                f"'{Path(expected_problem_path).name}'",
            )
        )
    lookup_name = cited_ref if cited_ref else name
    original = problem_axioms.get(lookup_name)
    if original is None:
        issues.append(
            ProvenanceIssue(name, f"no formula named '{lookup_name}' found in the problem file")
        )
        return issues

    if original.role != FormulaRole.AXIOM:
        issues.append(
            ProvenanceIssue(
                name, f"'{lookup_name}' in problem file has role '{original.role}', not 'axiom'"
            )
        )

    if not is_alpha_equivalent(proof_axiom.formula, original.formula):
        issues.append(
            ProvenanceIssue(
                name,
                f"formula content is not alpha-equivalent to '{lookup_name}' in the problem file",
            )
        )

    return issues
