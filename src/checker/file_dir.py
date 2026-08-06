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


def _normalized_path(path_str: str) -> Path:
    path = Path(path_str)
    try:
        return path.resolve()
    except OSError:
        return path


def _paths_match(cited_path: str, expected_path: str, strict_path_match: bool) -> bool:
    cited = Path(cited_path)
    expected = Path(expected_path)
    if strict_path_match:
        return _normalized_path(cited_path) == _normalized_path(expected_path)
    if cited.name == expected.name:
        return True
    return _normalized_path(cited_path) == _normalized_path(expected_path)


def check_axiom_provenance(
    proof_axiom: AnnotatedFormula,
    problem_axioms: dict[str, AnnotatedFormula],
    expected_problem_path: str,
    *,
    strict_path_match: bool = False,
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

    if not _paths_match(cited_path, expected_problem_path, strict_path_match):
        expectation = (
            f"expected exact path '{expected_problem_path}'"
            if strict_path_match
            else f"expected a file named '{Path(expected_problem_path).name}'"
        )
        issues.append(
            ProvenanceIssue(
                name,
                f"file(...) points to '{cited_path}', {expectation}",
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
