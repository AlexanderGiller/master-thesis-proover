"""Checker for existential_gen steps in proofs."""

from dataclasses import dataclass

from src.checker.formula_utils import flatten_prefix, match_template_to_instance
from src.parser.ast_nodes import AnnotatedFormula, JunctionFormula
from src.var_mapping import InferenceRule, InferenceStatus, Quantifier


@dataclass
class ExistentialGenIssue:
    step_name: str
    reason: str


def check_existential_gen(
    step: AnnotatedFormula, parent_step: AnnotatedFormula
) -> list[ExistentialGenIssue]:
    """Check whether a step is a valid existential generalization of its parent."""
    issues: list[ExistentialGenIssue] = []

    if step.inference is None:
        issues.append(
            ExistentialGenIssue(step.name, "existential_gen step must have an inference record")
        )
        return issues

    inf = step.inference
    if inf.rule != InferenceRule.EXISTENTIAL_GEN:
        issues.append(
            ExistentialGenIssue(step.name, f"rule must be 'existential_gen', got '{inf.rule}'")
        )

    if inf.status != InferenceStatus.THM:
        issues.append(
            ExistentialGenIssue(step.name, f"status must be 'thm', got '{inf.status}'")
        )

    existential_vars, child_body = flatten_prefix(step.formula, Quantifier.EXISTENTIAL)
    if not existential_vars:
        issues.append(
            ExistentialGenIssue(
                step.name,
                "existential_gen step must introduce at least one leading existential variable",
            )
        )
        return issues

    def _matches_generalization(target_formula: object) -> bool:
        """Check if child_body generalizes target_formula."""
        target_vars, target_inner = flatten_prefix(target_formula, Quantifier.EXISTENTIAL)
        if len(existential_vars) <= len(target_vars):
            return False
        new_count = len(existential_vars) - len(target_vars)
        new_vars = existential_vars[:new_count]
        preserved_vars = existential_vars[new_count:]
        bound_map = dict(zip(target_vars, preserved_vars))
        return match_template_to_instance(child_body, target_inner, set(new_vars), dict(bound_map))

    if not _matches_generalization(parent_step.formula):
        if isinstance(parent_step.formula, JunctionFormula) and any(
            _matches_generalization(operand) for operand in parent_step.formula.operands
        ):
            return issues
        issues.append(
            ExistentialGenIssue(
                step.name,
                "formula is not a valid existential generalization of the parent formula",
            )
        )

    return issues
